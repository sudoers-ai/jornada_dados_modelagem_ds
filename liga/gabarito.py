# -*- coding: utf-8 -*-
"""Aplica a resposta pronta de uma tabela:  make gabarito t=fs_cliente"""
import os
import sys

from liga import contrato
from liga.banco import C, F, R, RAIZ, V, executar, valor
from liga.conferir import conferiu


def aplicar(tabela):
    if tabela not in contrato.TABELAS:
        print("%s❌ Não conheço a tabela '%s'.%s As da trilha são: %s"
              % (R, tabela, F, ", ".join(contrato.TABELAS)))
        return False
    _, _, gabarito, deps = contrato.TABELAS[tabela]
    for dep in deps:
        if not valor("SELECT to_regclass('analytics.%s') IS NOT NULL" % dep):
            print("%s(antes, a dependência analytics.%s)%s" % (C, dep, F))
            aplicar(dep)
    with open(os.path.join(RAIZ, gabarito), encoding="utf-8") as fh:
        executar(fh.read(), mostrar=False)
    print("%s✅ analytics.%s criada a partir do gabarito (%s)%s" % (V, tabela, gabarito, F))
    return conferiu(tabela, silencioso=False)


if __name__ == "__main__":
    raise SystemExit(0 if aplicar(sys.argv[1] if len(sys.argv) > 1 else "") else 1)
