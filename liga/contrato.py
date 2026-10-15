# -*- coding: utf-8 -*-
"""
O contrato da camada analitica: modelagem/dbml/analytics.dbml.

Leitor do subconjunto de DBML usado no repositorio (o mesmo da Parte 3).
"""
import os
import re

from liga.banco import RAIZ

ARQUIVO = os.path.join(RAIZ, "modelagem", "dbml", "analytics.dbml")

# ordem da trilha: tabela -> (etapa, pasta do roteiro, gabarito, dependencias)
TABELAS = {
    "fs_cliente":       (3, "trilha/03_feature_table",  "modelagem/gabarito/01_fs_cliente.sql", []),
    "ds_pedido_fraude": (4, "trilha/04_tabela_de_treino", "modelagem/gabarito/02_ds_pedido_fraude.sql",
                         ["fs_cliente"]),
    "ds_cliente_mes":   (5, "trilha/05_painel",          "modelagem/gabarito/03_ds_cliente_mes.sql", []),
    "ds_peso_dia":      (6, "trilha/06_serie_temporal",  "modelagem/gabarito/04_ds_peso_dia.sql", []),
    "ds_entrega":       (7, "trilha/07_rotulo_por_regra", "modelagem/gabarito/05_ds_entrega.sql", []),
}


def _partes(texto):
    partes, atual, aspas = [], "", None
    for ch in texto:
        if aspas:
            atual += ch
            if ch == aspas:
                aspas = None
        elif ch in "'`\"":
            aspas = ch
            atual += ch
        elif ch == ",":
            partes.append(atual.strip())
            atual = ""
        else:
            atual += ch
    if atual.strip():
        partes.append(atual.strip())
    return partes


def ler():
    """Devolve {tabela: {"colunas": {nome: {"tipo", "nota"}}, "chave": [...]}}."""
    tabelas, tabela, em_indices = {}, None, False
    with open(ARQUIVO, encoding="utf-8") as fh:
        for bruta in fh.read().splitlines():
            linha = bruta.split("//")[0].strip()
            if not linha:
                continue
            m = re.match(r"^Table\s+(\w+)(\s*\[[^\]]*\])?\s*\{$", linha)
            if m:
                tabela = {"colunas": {}, "chave": []}
                tabelas[m.group(1)] = tabela
                continue
            if tabela is None:
                continue
            if linha.startswith("indexes"):
                em_indices = True
                continue
            if linha == "}":
                if em_indices:
                    em_indices = False
                else:
                    tabela = None
                continue
            if em_indices:
                m = re.match(r"^\(?([\w\s,]+)\)?\s*\[([^\]]*)\]$", linha)
                if m and "pk" in m.group(2):
                    tabela["chave"] = [c.strip() for c in m.group(1).split(",")]
                continue
            m = re.match(r"^(\w+)\s+([\w]+(?:\([\d,\s]+\))?)\s*(?:\[(.*)\])?$", linha)
            if m:
                nota = ""
                for a in _partes(m.group(3) or ""):
                    if a.lower() == "pk":
                        tabela["chave"] = tabela["chave"] + [m.group(1)]
                    if a.lower().startswith("note"):
                        nota = a.split(":", 1)[1].strip().strip("'")
                tabela["colunas"][m.group(1)] = {"tipo": m.group(2), "nota": nota}
    return tabelas


def familia(tipo):
    t = tipo.lower().split("(")[0]
    if t in ("varchar", "char", "text", "character", "character varying"):
        return "texto"
    if t in ("int", "integer", "smallint", "bigint"):
        return "inteiro"
    if t in ("numeric", "decimal", "double precision", "real"):
        return "número decimal"
    if t.startswith("timestamp"):
        return "timestamp"
    if t == "date":
        return "data"
    if t in ("boolean", "bool"):
        return "booleano"
    return t
