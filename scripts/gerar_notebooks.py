# -*- coding: utf-8 -*-
"""
Gera os notebooks da trilha (notebooks/*.ipynb) a partir das fontes em
scripts/notebooks/*.txt. So para quem MANTEM o repositorio.

    docker compose exec jupyter python scripts/gerar_notebooks.py

Formato da fonte: blocos separados por linhas `=== md` e `=== code`.
Uma celula de codigo com uma unica linha `@gabarito arquivo.sql` vira
`executar(\"\"\"<conteudo de modelagem/gabarito/arquivo.sql>\"\"\")`: o SQL do
notebook e o do gabarito sao, literalmente, o mesmo arquivo.
"""
import glob
import os

import nbformat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def celulas(texto):
    tipo, buf = None, []
    for linha in texto.splitlines():
        if linha.strip() in ("=== md", "=== code"):
            if tipo:
                yield tipo, "\n".join(buf).strip("\n")
            tipo, buf = linha.strip()[4:], []
        else:
            buf.append(linha)
    if tipo:
        yield tipo, "\n".join(buf).strip("\n")


def main():
    for fonte in sorted(glob.glob(os.path.join(RAIZ, "scripts", "notebooks", "*.txt"))):
        nb = nbformat.v4.new_notebook()
        nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                       "language_info": {"name": "python"}}
        with open(fonte, encoding="utf-8") as fh:
            for tipo, conteudo in celulas(fh.read()):
                if tipo == "md":
                    nb.cells.append(nbformat.v4.new_markdown_cell(conteudo))
                    continue
                if conteudo.startswith("@gabarito "):
                    arquivo = conteudo.split(None, 1)[1].strip()
                    with open(os.path.join(RAIZ, "modelagem", "gabarito", arquivo), encoding="utf-8") as g:
                        conteudo = 'executar("""\n%s\n""")' % g.read().strip()
                nb.cells.append(nbformat.v4.new_code_cell(conteudo))
        saida = os.path.join(RAIZ, "notebooks", os.path.basename(fonte)[:-4] + ".ipynb")
        nbformat.write(nb, saida)
        print("  escrito:", os.path.relpath(saida, RAIZ), "(%d células)" % len(nb.cells))


if __name__ == "__main__":
    main()
