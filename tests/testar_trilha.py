# -*- coding: utf-8 -*-
"""
Executa os notebooks da trilha, em ordem, do jeito que o aluno faria.

Ferramenta de quem MANTEM o repositorio:

    make testar-trilha                  (apaga o que o aluno fez e roda tudo)
    make testar-trilha args=--salvar    (grava os notebooks executados em saida/)

Os notebooks originais NAO sao alterados (o aluno os recebe sem saida).
Falha se qualquer celula der erro ou se alguma conferencia nao fechar.
"""
import glob
import os
import sys
import time

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from liga.banco import R, V, F, C, executar        # noqa: E402
from liga.conferir import conferiu                 # noqa: E402


def main():
    salvar = "--salvar" in sys.argv
    print("Limpando o trabalho do aluno (schemas analytics, legado e referencia)...")
    executar("DROP SCHEMA IF EXISTS analytics CASCADE; DROP SCHEMA IF EXISTS legado CASCADE; "
             "DROP SCHEMA IF EXISTS referencia CASCADE; CREATE SCHEMA analytics; CREATE SCHEMA legado; "
             "CREATE SCHEMA referencia;", mostrar=False)
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "notebooks", "*.ipynb"))):
        nome = os.path.basename(caminho)
        inicio = time.time()
        nb = nbformat.read(caminho, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
        try:
            ep.preprocess(nb, {"metadata": {"path": os.path.join(RAIZ, "notebooks")}})
        except Exception as e:                      # noqa: BLE001
            print("%s❌ %s quebrou:%s\n%s" % (R, nome, F, str(e)[-1500:]))
            return 1
        print("  %s✅%s %-28s %s(%.0fs)%s" % (V, F, nome, C, time.time() - inicio, F))
        if salvar:
            os.makedirs(os.path.join(RAIZ, "saida"), exist_ok=True)
            nbformat.write(nb, os.path.join(RAIZ, "saida", nome))
    print()
    ok = conferiu("todas")
    print(("%s✅ Trilha executada e todas as tabelas conferidas.%s" if ok
           else "%s❌ Alguma tabela não conferiu.%s") % (V if ok else R, F))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
