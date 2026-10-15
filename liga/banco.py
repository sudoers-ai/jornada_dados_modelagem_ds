# -*- coding: utf-8 -*-
"""Conexao com o Data Warehouse."""
import os
import time
import warnings

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore", category=UserWarning)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V, A, R, C, N, F = "\033[92m", "\033[93m", "\033[91m", "\033[90m", "\033[1m", "\033[0m"

_CFG = dict(host=os.getenv("PGHOST", "postgres"), dbname=os.getenv("PGDATABASE", "liga_sudoers_dw"),
            user=os.getenv("PGUSER", "sudoers"), password=os.getenv("PGPASSWORD", "password"))
_MOTOR = None


def motor():
    global _MOTOR
    if _MOTOR is None:
        _MOTOR = create_engine("postgresql+psycopg2://%(user)s:%(password)s@%(host)s/%(dbname)s" % _CFG)
    return _MOTOR


def conexao():
    con = psycopg2.connect(**_CFG)
    con.autocommit = True
    return con


def sql(consulta, **parametros):
    """Roda um SELECT e devolve um DataFrame."""
    with motor().connect() as con:
        return pd.read_sql(text(consulta), con, params=parametros or None)


def valor(consulta):
    """Roda um SELECT que devolve UM valor."""
    con = conexao()
    try:
        cur = con.cursor()
        cur.execute(consulta)
        linha = cur.fetchone()
        return linha[0] if linha else None
    finally:
        con.close()


class ErroNoBanco(Exception):
    """O banco recusou o comando. A mensagem diz por que."""


def executar(comandos, mostrar=True):
    """Roda um ou mais comandos SQL (CREATE TABLE, DROP, ALTER...)."""
    inicio = time.time()
    con = conexao()
    try:
        cur = con.cursor()
        cur.execute("SET client_min_messages = warning")
        cur.execute(comandos)
    except psycopg2.Error as e:
        msg = str(e).strip().splitlines()[0]
        print("%s❌ O banco recusou o comando:%s %s" % (R, F, msg))
        if e.diag and e.diag.message_hint:
            print("   dica do PostgreSQL: %s" % e.diag.message_hint)
        raise ErroNoBanco(msg) from None
    finally:
        con.close()
    if mostrar:
        print("%s✅ Pronto%s %s(%.1fs)%s" % (V, F, C, time.time() - inicio, F))
