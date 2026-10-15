# -*- coding: utf-8 -*-
"""
A prova de cada etapa: compara a SUA tabela com o modelo.

    make conferir t=fs_cliente        (no terminal)
    conferir("fs_cliente")            (no notebook)
    make conferir                     (todas)

Duas camadas, como na Parte 3:
  1. ESTRUTURA - a tabela existe, com as colunas e tipos do contrato
     (modelagem/dbml/analytics.dbml), e a chave nao se repete (o grao).
  2. CONTEUDO - linha a linha e coluna a coluna, igual a referencia. Como os
     dados sao deterministicos, o repositorio sabe exatamente qual e a tabela
     certa. Se uma feature sua usar informacao do futuro, o valor nao bate e
     a conferencia aponta a coluna, com um exemplo.
"""
import os
import sys

from liga import contrato
from liga.banco import A, C, F, N, R, RAIZ, V, conexao

# Dicas para os erros mais comuns, por coluna
DICAS = {
    ("fs_cliente", "uf"): "a UF tem que ser a da versão de dim_pessoas que valia naquele dia "
                          "(data >= dt_inicio e data < dt_fim)",
    ("fs_cliente", "qtd_pedidos_total"): "conte só os dias ANTERIORES: a janela termina em 1 PRECEDING, "
                                         "e não em CURRENT ROW",
    ("fs_cliente", "qtd_pedidos_30d"): "30 dias ANTERIORES: ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING",
    ("fs_cliente", "valor_medio_pedido"): "média dos pedidos ANTERIORES ao dia; nulo se nunca comprou",
    ("fs_cliente", "dias_desde_ultimo_pedido"): "o último pedido ANTES do dia; nulo se nunca comprou",
    ("fs_cliente", "qtd_dispositivos"): "aparelhos usados pela 1ª vez ANTES do dia",
    ("ds_pedido_fraude", "valor_total"): "some os ITENS do pedido (fato_pedidos tem uma linha por item)",
    ("ds_pedido_fraude", "is_dispositivo_novo"): "olhe só os usos do aparelho ANTERIORES a esta compra",
    ("ds_pedido_fraude", "qtd_outras_contas_no_dispositivo"):
        "conte só as OUTRAS pessoas que usaram o aparelho ANTES desta compra. Contar todo mundo é usar o futuro",
    ("ds_pedido_fraude", "is_fraude"): "o rótulo fica NULO nos pedidos dos últimos 7 dias antes da foto",
    ("ds_pedido_fraude", "particao"): "treino: antes de (foto - 60 dias); teste: até (foto - 7 dias); "
                                      "sem_rotulo: o resto",
    ("ds_pedido_fraude", "is_uf_diferente_do_cadastro"): "compare com a UF de fs_cliente NO DIA da compra",
    ("ds_cliente_mes", "qtd_pedidos"): "sem cancelados e devolvidos; 0 nos meses sem compra (a grade!)",
    ("ds_cliente_mes", "comprou_mes_seguinte"): "use o mês SEGUINTE do calendário (LEAD na grade completa); "
                                                "nulo no último mês",
    ("ds_peso_dia", "peso_kg_7_dias_antes"): "LAG de 7 LINHAS só é 7 DIAS se a grade não tiver buracos",
    ("ds_peso_dia", "media_7_dias_anteriores"): "ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING: sem o próprio dia",
    ("ds_entrega", "atrasou"): "nulo para saídas dos últimos 10 dias antes da foto (censura)",
    ("ds_entrega", "taxa_atraso_transportadora"): "só entregas CONCLUÍDAS ANTES desta saída",
}


def _q(cur, consulta):
    cur.execute(consulta)
    return cur.fetchall()


def _colunas_reais(cur, schema, tabela):
    linhas = _q(cur, "SELECT column_name, data_type FROM information_schema.columns "
                     "WHERE table_schema = '%s' AND table_name = '%s'" % (schema, tabela))
    return {c: t for c, t in linhas}


def construir_referencia(cur, tabela):
    """Constroi referencia.<tabela> (e as dependencias) a partir do gabarito, se faltar."""
    _, _, gabarito, deps = contrato.TABELAS[tabela]
    for dep in deps:
        construir_referencia(cur, dep)
    if _colunas_reais(cur, "referencia", tabela):
        return
    with open(os.path.join(RAIZ, gabarito), encoding="utf-8") as fh:
        texto = fh.read().replace("analytics.", "referencia.")
    cur.execute("CREATE SCHEMA IF NOT EXISTS referencia")
    cur.execute("SET client_min_messages = warning")
    cur.execute(texto)


def _fmt(n):
    return "{:,}".format(n).replace(",", ".")


def conferir(tabela=None):
    """Confere uma tabela (ou todas) e mostra o relatorio."""
    conferiu(tabela, silencioso=False)


def conferiu(tabela=None, silencioso=True):
    """Confere e devolve True se estiver tudo certo (sem imprimir, por padrao)."""
    if tabela in (None, "", "todas"):
        resultados = [conferiu(t, silencioso) for t in contrato.TABELAS]
        return all(resultados)
    if tabela not in contrato.TABELAS:
        print("%s❌ Não conheço a tabela '%s'.%s As da trilha são: %s"
              % (R, tabela, F, ", ".join(contrato.TABELAS)))
        return False

    etapa, pasta, _, deps = contrato.TABELAS[tabela]
    modelo = contrato.ler()[tabela]
    chave = modelo["chave"]
    linhas_saida, pend = [], []

    def ok(texto):
        linhas_saida.append("  %s✅%s %s" % (V, F, texto))

    def erro(texto, *detalhes):
        pend.append(texto)
        linhas_saida.append("  %s❌%s %s" % (R, F, texto))
        for d in detalhes:
            linhas_saida.append("       %s" % d)

    con = conexao()
    cur = con.cursor()
    try:
        reais = _colunas_reais(cur, "analytics", tabela)
        if not reais:
            erro("analytics.%s ainda não existe" % tabela,
                 "ela é construída na etapa %d: %s/README.md" % (etapa, pasta))
            return _final(tabela, etapa, linhas_saida, pend, silencioso)
        ok("a tabela existe")

        # ---------------------------------------------------- estrutura
        faltando = [c for c in modelo["colunas"] if c not in reais]
        tipo_errado = [(c, contrato.familia(modelo["colunas"][c]["tipo"]), contrato.familia(reais[c]))
                       for c in modelo["colunas"] if c in reais
                       and contrato.familia(modelo["colunas"][c]["tipo"]) != contrato.familia(reais[c])]
        sobrando = [c for c in reais if c not in modelo["colunas"]]
        if faltando:
            erro("faltam colunas do modelo: %s" % ", ".join(faltando))
        for c, esperado, achado in tipo_errado:
            erro("%s: tipo esperado %s, encontrado %s" % (c, esperado, achado))
        if not faltando and not tipo_errado:
            ok("as %d colunas do modelo estão lá, com os tipos certos" % len(modelo["colunas"]))
        if sobrando:
            linhas_saida.append("  %s⚠️  colunas a mais (não impedem): %s%s" % (A, ", ".join(sobrando), F))
        if faltando or any(k not in reais for k in chave):
            return _final(tabela, etapa, linhas_saida, pend, silencioso)

        # ---------------------------------------------------------- grao
        lista_chave = ", ".join(chave)
        total, distintos = _q(cur, "SELECT count(*), count(DISTINCT (%s)) FROM analytics.%s"
                                   % (lista_chave, tabela))[0]
        if total != distintos:
            erro("grão: a chave (%s) se repete — %s linhas para %s chaves diferentes"
                 % (lista_chave, _fmt(total), _fmt(distintos)),
                 "um JOIN multiplicou linhas. Agregue ANTES de juntar, ou junte pela chave certa.")
        else:
            ok("grão: 1 linha por (%s), nenhuma repetida" % lista_chave)

        # ------------------------------------------------------ conteudo
        construir_referencia(cur, tabela)
        esperado = _q(cur, "SELECT count(*) FROM referencia.%s" % tabela)[0][0]
        on = " AND ".join("a.%s = r.%s" % (k, k) for k in chave)
        so_aluno, so_ref = _q(cur, """
            SELECT count(*) FILTER (WHERE r.%s IS NULL), count(*) FILTER (WHERE a.%s IS NULL)
            FROM (SELECT DISTINCT %s FROM analytics.%s) a
            FULL JOIN (SELECT %s FROM referencia.%s) r ON %s"""
            % (chave[0], chave[0], lista_chave, tabela, lista_chave, tabela, on))[0]
        if total == esperado and not so_aluno and not so_ref:
            ok("linhas: %s (esperado %s)" % (_fmt(total), _fmt(esperado)))
        else:
            detalhes = []
            if so_ref:
                detalhes.append("faltam %s chaves que deveriam estar na tabela" % _fmt(so_ref))
            if so_aluno:
                detalhes.append("sobram %s chaves que não deveriam estar" % _fmt(so_aluno))
            erro("linhas: %s (esperado %s)" % (_fmt(total), _fmt(esperado)), *detalhes)

        comparaveis = [c for c in modelo["colunas"] if c not in chave and c in reais]
        partes = []
        for c in comparaveis:
            if contrato.familia(modelo["colunas"][c]["tipo"]) == "número decimal":
                partes.append("count(*) FILTER (WHERE (a.%s IS NULL) <> (r.%s IS NULL) "
                              "OR abs(a.%s - r.%s) > 0.011)" % (c, c, c, c))
            else:
                partes.append("count(*) FILTER (WHERE a.%s IS DISTINCT FROM r.%s)" % (c, c))
        base = "FROM analytics.%s a JOIN referencia.%s r ON %s" % (tabela, tabela, on)
        contagens = _q(cur, "SELECT %s %s" % (", ".join(partes), base))[0]
        erradas = [(c, n) for c, n in zip(comparaveis, contagens) if n]
        if not erradas:
            ok("conteúdo: as %d colunas batem com a referência, linha a linha" % len(comparaveis))
        for c, n in erradas:
            if contrato.familia(modelo["colunas"][c]["tipo"]) == "número decimal":
                filtro = "(a.%s IS NULL) <> (r.%s IS NULL) OR abs(a.%s - r.%s) > 0.011" % (c, c, c, c)
            else:
                filtro = "a.%s IS DISTINCT FROM r.%s" % (c, c)
            ex = _q(cur, "SELECT %s, a.%s, r.%s %s WHERE %s ORDER BY %s LIMIT 1"
                         % (", ".join("a.%s" % k for k in chave), c, c, base, filtro,
                            ", ".join("a.%s" % k for k in chave)))[0]
            onde = ", ".join("%s=%s" % (k, v) for k, v in zip(chave, ex[:len(chave)]))
            detalhes = ["exemplo: %s → sua tabela: %s, esperado: %s" % (onde, ex[-2], ex[-1])]
            if (tabela, c) in DICAS:
                detalhes.append("dica: " + DICAS[(tabela, c)])
            erro("%s: %s linhas diferentes da referência" % (c, _fmt(n)), *detalhes)
    finally:
        cur.close()
        con.close()
    return _final(tabela, etapa, linhas_saida, pend, silencioso)


def _final(tabela, etapa, linhas_saida, pend, silencioso):
    if not silencioso:
        print()
        print("%sConferindo analytics.%s%s  %s(etapa %d)%s" % (N, tabela, F, C, etapa, F))
        print()
        print("\n".join(linhas_saida))
        print()
        if pend:
            print("%s❌ %d pendência(s) em analytics.%s.%s Corrija e confira de novo."
                  % (R, len(pend), tabela, F))
            print("   %sTravou? `make gabarito t=%s` aplica a resposta pronta.%s" % (C, tabela, F))
        else:
            print("%s✅ analytics.%s conferida. Etapa %d concluída!%s" % (V, tabela, etapa, F))
        print()
    return not pend


def main():
    tabela = sys.argv[1] if len(sys.argv) > 1 else "todas"
    return 0 if conferiu(tabela, silencioso=False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
