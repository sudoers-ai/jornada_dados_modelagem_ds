# -*- coding: utf-8 -*-
"""
Treina um modelo na sua tabela e responde: ele funcionaria em producao?

    make avaliar t=legado      (o notebook herdado)
    make avaliar t=fraude      (a sua analytics.ds_pedido_fraude)
    avaliar("fraude")          (no notebook)

O modelo e SEMPRE o mesmo, simples e fixo (voce nao o escreve): a disciplina
e de modelagem de DADOS. O que muda e a tabela que voce entrega a ele.

Duas medidas:

  NO NOTEBOOK   - como a tabela costuma ser avaliada por quem a construiu:
                  com a divisao de treino e teste que a propria tabela traz
                  (coluna `particao`) ou, se nao houver, sorteando as linhas.

  EM PRODUCAO   - o que acontece de verdade: o modelo e treinado com o
                  passado e da nota aos pedidos de julho e agosto, com os
                  valores de cada coluna QUE EXISTIAM NO MOMENTO DA COMPRA.

Se as duas medidas concordam, a tabela e honesta. Se o notebook e muito
melhor que a producao, alguma coluna esta usando o futuro.
"""
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

from liga import contrato
from liga.banco import A, C, F, N, R, V, conexao, sql
from liga.conferir import construir_referencia

warnings.filterwarnings("ignore")

TABELAS = {"legado": "legado.dataset_fraude", "fraude": "analytics.ds_pedido_fraude"}
IGNORAR = {"id_pedido", "id_pessoa", "dt_venda", "is_fraude", "particao"}
ULTIMO = None        # o resultado da ultima avaliacao, para quem quiser usar no notebook

# Colunas do notebook herdado que mudam DEPOIS da compra. Para elas, a producao
# usa o valor que existia no momento da compra. As outras colunas do herdado
# (valor, hora, forma de pagamento...) ja eram conhecidas na compra e ficam
# como estao - os erros delas sao de GRAO, nao de tempo.
MOMENTO_DA_COMPRA_LEGADO = ["status", "taxa_fraude_cliente", "qtd_contas_dispositivo", "uf_cliente"]
REVISAO = 0.10       # a equipe antifraude consegue revisar 10% dos pedidos


def _producao(cur):
    """referencia.producao_fraude: cada coluna conhecida, com o valor do MOMENTO DA COMPRA."""
    construir_referencia(cur, "ds_pedido_fraude")
    cur.execute("SELECT to_regclass('referencia.producao_fraude')")
    if cur.fetchone()[0]:
        return
    cur.execute("""
        CREATE TABLE referencia.producao_fraude AS
        WITH pedidos AS (
            SELECT f.id_pedido, min(f.sk_pessoa) AS sk_pessoa, min(f.dt_venda) AS dt_venda,
                   bool_or(f.is_fraude) AS is_fraude, max(f.dt_fraude) AS dt_fraude
            FROM public.fato_pedidos f GROUP BY f.id_pedido
        ),
        com_pessoa AS (
            SELECT p.*, d.id AS id_pessoa FROM pedidos p JOIN public.dim_pessoas d ON d.sk_pessoa = p.sk_pessoa
        )
        SELECT r.*,
               -- nomes usados no notebook herdado, com o valor que existia na hora da compra:
               'criado'::text                              AS status,
               fs.uf::text                                 AS uf_cliente,
               1 + r.qtd_outras_contas_no_dispositivo      AS qtd_contas_dispositivo,
               COALESCE((SELECT avg(CASE WHEN a.is_fraude AND a.dt_fraude < r.dt_venda THEN 1.0 ELSE 0 END)
                           FROM com_pessoa a
                          WHERE a.id_pessoa = r.id_pessoa AND a.dt_venda < r.dt_venda), 0)
                                                           AS taxa_fraude_cliente,
               v.is_fraude                                 AS rotulo_verdadeiro
        FROM referencia.ds_pedido_fraude r
        JOIN referencia.fs_cliente fs ON fs.id_pessoa = r.id_pessoa AND fs.data = r.dt_venda::date
        JOIN com_pessoa v ON v.id_pedido = r.id_pedido
    """)


def _matriz(df, colunas, referencia_colunas=None):
    x = pd.get_dummies(df[colunas], dtype=float)
    if referencia_colunas is not None:
        x = x.reindex(columns=referencia_colunas, fill_value=0.0)
    return x.astype(float).fillna(-1)


def _treinar(x, y):
    modelo = HistGradientBoostingClassifier(random_state=0)
    modelo.fit(x, y)
    return modelo


def _medidas(y, p):
    y = np.asarray(y).astype(int)
    k = max(1, int(round(len(p) * REVISAO)))
    pegas = y[np.argsort(-p)[:k]].sum() / max(y.sum(), 1)
    return roc_auc_score(y, p), average_precision_score(y, p), pegas


def avaliar(qual="fraude"):
    """Mostra o relatorio. O resultado fica em liga.avaliar.ULTIMO."""
    global ULTIMO
    ULTIMO = _avaliar(qual)


def _avaliar(qual):
    if qual not in TABELAS:
        print("uso: avaliar('legado') ou avaliar('fraude')")
        return None
    nome = TABELAS[qual]
    con = conexao()
    cur = con.cursor()
    cur.execute("SELECT to_regclass('%s')" % nome)
    if not cur.fetchone()[0]:
        quando = "na etapa 2 (notebooks/02_notebook_herdado.ipynb)" if qual == "legado" \
            else "na etapa 4 (notebooks/04_tabela_de_treino.ipynb)"
        print("%s❌ %s ainda não existe.%s Ela é criada %s." % (R, nome, F, quando))
        con.close()
        return None
    cur.execute("SET client_min_messages = warning")
    _producao(cur)
    con.close()

    tabela = sql("SELECT * FROM %s" % nome)
    prod = sql("SELECT * FROM referencia.producao_fraude").set_index("id_pedido")
    tabela = tabela[tabela.is_fraude.notna()].copy()
    tabela["is_fraude"] = tabela.is_fraude.astype(int)
    colunas = [c for c in tabela.columns if c not in IGNORAR]

    foto = prod.dt_venda.max().normalize()
    inicio_teste, fim_teste = foto - pd.Timedelta(days=60), foto - pd.Timedelta(days=7)

    # ------------------------------------------------- 1) no notebook
    if "particao" in tabela.columns:
        tr, te = tabela[tabela.particao == "treino"], tabela[tabela.particao == "teste"]
        como = "divisão da própria tabela (coluna particao)"
    else:
        tr, te = train_test_split(tabela, test_size=0.25, random_state=42)
        como = "linhas sorteadas (train_test_split)"
    x_tr = _matriz(tr, colunas)
    m = _treinar(x_tr, tr.is_fraude)
    nb = _medidas(te.is_fraude, m.predict_proba(_matriz(te, colunas, x_tr.columns))[:, 1])

    # ------------------------------------------------ 2) em producao
    passado = tabela[tabela.dt_venda < inicio_teste]
    x_tr = _matriz(passado, colunas)
    m = _treinar(x_tr, passado.is_fraude)
    ids = prod[(prod.dt_venda >= inicio_teste) & (prod.dt_venda < fim_teste)].index
    base = tabela.drop_duplicates("id_pedido").set_index("id_pedido")
    ids_presentes = [i for i in ids if i in base.index]
    agora = base.loc[ids_presentes, colunas].copy()
    if qual == "fraude":
        do_momento = [c for c in colunas if c in contrato.ler()["ds_pedido_fraude"]["colunas"]]
    else:
        do_momento = [c for c in colunas if c in MOMENTO_DA_COMPRA_LEGADO]
    trocadas = []
    for c in do_momento:
        if c in prod.columns:
            antes = agora[c]
            depois = prod.loc[ids_presentes, c]
            diferentes = (antes.astype(str) != depois.astype(str)).mean()
            if diferentes > 0.01:
                trocadas.append((c, diferentes))
            agora[c] = depois.values
    y_prod = prod.loc[ids_presentes, "rotulo_verdadeiro"].astype(int)
    pr = _medidas(y_prod, m.predict_proba(_matriz(agora, colunas, x_tr.columns))[:, 1])

    # ------------------------------------------------------ relatorio
    linhas_por_pedido = len(tabela) / max(tabela.id_pedido.nunique(), 1)
    print()
    print("%sAvaliando %s%s" % (N, nome, F))
    print("%s  modelo fixo: HistGradientBoostingClassifier, com as %d colunas da tabela%s"
          % (C, len(colunas), F))
    print()
    print("                    AUC    PR-AUC   fraudes pegas revisando 10% dos pedidos")
    print("  no notebook      %.3f   %.3f     %3.0f%%   %s(%s)%s" % (nb[0], nb[1], 100 * nb[2], C, como, F))
    print("  em produção      %.3f   %.3f     %3.0f%%   %s(pedidos de jul-ago, com o que se sabia na compra)%s"
          % (pr[0], pr[1], 100 * pr[2], C, F))
    print()
    if linhas_por_pedido > 1.001:
        print("  %s⚠️  %.2f linhas por pedido:%s o grão não é o pedido. Um mesmo pedido cai no treino e"
              % (A, linhas_por_pedido, F))
        print("     no teste ao mesmo tempo, e o modelo é testado em pedidos que já viu.")
    if trocadas:
        print("  %s⚠️  colunas que NÃO tinham este valor no momento da compra:%s" % (A, F))
        for c, frac in sorted(trocadas, key=lambda t: -t[1]):
            print("       %-36s %3.0f%% dos pedidos mudam" % (c, 100 * frac))
    print()
    queda = nb[0] - pr[0]
    if queda > 0.05:
        print("%s❌ O modelo perde %.0f pontos de AUC entre o notebook e a produção.%s" % (R, 100 * queda, F))
        print("   O notebook estava medindo o futuro, não o modelo.")
    else:
        print("%s✅ Notebook e produção concordam.%s A tabela só usa o que existia no momento da compra."
              % (V, F))
    print()
    return {"notebook": nb, "producao": pr, "colunas_do_futuro": [c for c, _ in trocadas]}


def main():
    return 0 if _avaliar(sys.argv[1] if len(sys.argv) > 1 else "fraude") is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
