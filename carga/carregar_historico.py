# -*- coding: utf-8 -*-
"""
Grava no banco TRANSACIONAL o historico de pedidos (180 dias).

E o mesmo processo da Parte 3 (liga_sudoers_historico.py), com uma
diferenca: as datas NAO sao deslocadas para "hoje". A foto e sempre a de
01/09/2026. Assim, toda tabela que voce construir tera exatamente os mesmos
numeros deste roteiro, em qualquer dia em que voce rodar.

Voce nao roda este arquivo direto: ele e chamado pelo `make carregar`.
"""
import io
import os
import sys

import psycopg2

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from gerador import extensao_modelagem as ext_mod           # noqa: E402
from gerador.liga_sudoers_gen import gerar_universo         # noqa: E402
from gerador.ruido_ds import aplicar_ruido                  # noqa: E402


def copiar(cur, tabela, colunas, linhas):
    buf = io.StringIO()
    n = 0
    for linha in linhas:
        buf.write("\t".join(
            "\\N" if v is None else str(v).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")
            for v in linha))
        buf.write("\n")
        n += 1
    buf.seek(0)
    cur.copy_expert("COPY public.%s (%s) FROM STDIN" % (tabela, ", ".join(colunas)), buf)
    return n


def carregar(cur, u, ext):
    gravado = {}
    for id_produto, peso in ext["pesos"].items():
        cur.execute("UPDATE public.produtos SET peso_gramas = %s WHERE id = %s", (peso, id_produto))
    gravado["produtos (peso)"] = len(ext["pesos"])
    gravado["dispositivos"] = copiar(
        cur, "dispositivos", ["device_id", "modelo", "sistema", "created_at", "updated_at"],
        ((x["device_id"], x["modelo"], x["sistema"], x["created_at"], x["created_at"]) for x in ext["dispositivos"]))
    gravado["enderecos"] = copiar(
        cur, "enderecos",
        ["id", "id_pessoa", "logradouro", "cidade", "uf", "cep", "is_principal", "created_at", "updated_at"],
        ((e["id"], e["id_pessoa"], e["logradouro"], e["cidade"], e["uf"], e["cep"], e["is_principal"],
          e["created_at"], e["updated_at"]) for e in ext["enderecos"]))
    gravado["transportadoras"] = copiar(
        cur, "transportadoras", ["id", "nome", "cnpj", "custo_por_kg"],
        ((t["id"], t["nome"], t["cnpj"], t["custo_por_kg"]) for t in ext["transportadoras"]))
    gravado["pedidos"] = copiar(
        cur, "pedidos",
        ["id", "id_pessoa", "dt_venda", "valor_total", "id_endereco_entrega", "status", "created_at", "updated_at"],
        ((p["id"], p["id_pessoa"], ext["pedidos"][p["id"]]["dt_venda"], p["valor_total"],
          ext["pedidos"][p["id"]]["id_endereco_entrega"], ext["pedidos"][p["id"]]["status"],
          ext["pedidos"][p["id"]]["dt_venda"], ext["pedidos"][p["id"]]["dt_ultimo_evento"]) for p in u.pedidos))
    gravado["itens_pedidos"] = copiar(
        cur, "itens_pedidos", ["id_pedido", "id_produto", "qtde", "valor_total", "created_at", "updated_at"],
        ((p["id"], it["id_produto"], it["qtde"], it["valor_total"],
          ext["pedidos"][p["id"]]["dt_venda"], ext["pedidos"][p["id"]]["dt_venda"])
         for p in u.pedidos for it in p["itens"]))

    def auditoria():
        for p in u.pedidos:
            a, e = p["auditoria"], ext["pedidos"][p["id"]]
            yield (p["id"], a["dispositivo"], a["geohash"], a["telefone"], a["device_id"], a["uf"],
                   e["fraude_confirmada"], e["motivo_fraude"], e["dt_fraude"],
                   e["dt_venda"], e["dt_fraude"] or e["dt_venda"])
    gravado["auditoria_pedidos"] = copiar(
        cur, "auditoria_pedidos",
        ["id_pedido", "dispositivo", "geohash", "telefone", "device_id", "uf", "is_fraude", "motivo_fraude",
         "dt_fraude", "created_at", "updated_at"], auditoria())
    gravado["pagamentos"] = copiar(
        cur, "pagamentos",
        ["id", "id_pedido", "forma", "parcelas", "valor", "status", "dt_pagamento", "created_at", "updated_at"],
        ((g["id"], g["id_pedido"], g["forma"], g["parcelas"], g["valor"], g["status"], g["dt_pagamento"],
          g["created_at"], g["updated_at"]) for g in ext["pagamentos"]))
    gravado["status_pedidos"] = copiar(
        cur, "status_pedidos", ["id_pedido", "status", "dt_evento", "created_at", "updated_at"],
        ((s["id_pedido"], s["status"], s["dt_evento"], s["dt_evento"], s["dt_evento"]) for s in ext["status"]))
    gravado["transportes"] = copiar(
        cur, "transportes",
        ["id", "id_transportadora", "placa", "peso_total_gramas", "valor_frete", "dt_saida",
         "dt_entrega_prevista", "dt_entrega", "created_at", "updated_at"],
        ((t["id"], t["id_transportadora"], t["placa"], t["peso_total_gramas"], t["valor_frete"], t["dt_saida"],
          t["dt_entrega_prevista"], t["dt_entrega"], t["dt_saida"], t["dt_entrega"] or t["dt_saida"])
         for t in ext["transportes"]))
    gravado["carga_pedidos"] = copiar(
        cur, "carga_pedidos", ["id_transporte", "id_pedido", "created_at", "updated_at"],
        ((c["id_transporte"], c["id_pedido"], c["dt"], c["dt"]) for c in ext["cargas"]))
    for tabela in ("pedidos", "enderecos", "transportadoras", "transportes", "pagamentos"):
        cur.execute("SELECT setval(pg_get_serial_sequence('public.%s', 'id'), "
                    "(SELECT COALESCE(max(id), 1) FROM public.%s))" % (tabela, tabela))
    return gravado


def main():
    conn = psycopg2.connect(host=os.getenv("PGHOST", "postgres"), dbname="liga_sudoers",
                            user="sudoers", password="password")
    cur = conn.cursor()
    u = gerar_universo()
    ruido = aplicar_ruido(u)       # o que torna o problema realista (veja gerador/ruido_ds.py)
    gravado = carregar(cur, u, ext_mod.estender(u))
    conn.commit()
    for t, n in gravado.items():
        print("     %-22s %6d" % (t, n))
    print("     ruido: " + ", ".join("%s=%d" % kv for kv in ruido.items()))
    conn.close()


if __name__ == "__main__":
    main()
