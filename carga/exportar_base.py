# -*- coding: utf-8 -*-
"""
Gera carga/ddl/02_oltp_dados_base.sql a partir do gerador canonico.

So para quem MANTEM o repositorio. Diferente da Parte 3, aqui as datas sao
FIXAS (a "foto" do DW e de 01/09/2026, o "hoje" do gerador): assim toda
tabela que o aluno constroi tem exatamente os mesmos numeros, em qualquer dia.

    docker compose exec jupyter python carga/exportar_base.py
"""
import os
import sys
from datetime import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from gerador.liga_sudoers_gen import gerar_universo  # noqa: E402

SAIDA = os.path.join(RAIZ, "carga", "ddl", "02_oltp_dados_base.sql")


def q(v):
    return "'" + str(v).replace("'", "''") + "'"


def main():
    u = gerar_universo()
    with open(SAIDA, "w", encoding="utf-8") as fh:
        w = fh.write
        w("-- GERADO por carga/exportar_base.py (semente=%d). Nao edite a mao.\n" % u.semente)
        w("-- Cadastro base do transacional, com datas fixas.\n\n")
        for c in u.categorias:
            w("INSERT INTO public.categorias (id, descricao) VALUES (%d, %s);\n" % (c["id"], q(c["descricao"])))
        w("SELECT setval('public.categorias_id_seq', %d);\n\n" % len(u.categorias))
        for p in u.produtos:
            w("INSERT INTO public.produtos (id, id_categoria, descricao, valor_unit) VALUES (%d, %d, %s, %s);\n"
              % (p["id"], p["id_categoria"], q(p["descricao"]), p["valor_unit"]))
        w("SELECT setval('public.produtos_id_seq', %d);\n\n" % len(u.produtos))
        for p in u.pessoas:
            criado = datetime.fromisoformat(p["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
            w("INSERT INTO public.pessoas (id, nome, sexo, dt_nasc, created_at, updated_at) "
              "VALUES (%d, %s, %s, %s, %s, %s);\n"
              % (p["id"], q(p["nome"]), q(p["sexo"]), q(p["dt_nasc"]), q(criado), q(criado)))
    print("escrito:", SAIDA)


if __name__ == "__main__":
    main()
