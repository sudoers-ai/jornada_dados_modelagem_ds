# -*- coding: utf-8 -*-
"""
Confere se a documentacao, os notebooks e os gabaritos dizem a MESMA coisa.

Ferramenta de quem MANTEM o repositorio. Roda sem banco e sem Docker:

    python3 tests/conferir_docs.py

O que e conferido:
  1. todo link relativo e toda imagem citada nos .md e nos notebooks existe;
  2. todo `make <alvo>` citado existe no Makefile;
  3. todo `t=<tabela>` citado e uma tabela (ou avaliacao) que existe;
  4. cada notebook traz, na celula de construcao, o SQL IGUAL ao gabarito;
  5. os notebooks estao em dia com as fontes em scripts/notebooks/.
"""
import json
import os
import re
import sys
from urllib.parse import unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V, R, F = "\033[92m", "\033[91m", "\033[0m"
erros = []
IGNORAR_PASTAS = {".git", "saida", "node_modules", ".ipynb_checkpoints"}


def ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as fh:
        return fh.read()


def arquivos(ext):
    for raiz, pastas, nomes in os.walk(RAIZ):
        pastas[:] = [p for p in pastas if p not in IGNORAR_PASTAS]
        for n in nomes:
            if n.endswith(ext):
                yield os.path.relpath(os.path.join(raiz, n), RAIZ)


def textos():
    """(arquivo, texto) dos .md e das celulas markdown dos notebooks."""
    for md in arquivos(".md"):
        yield md, ler(md)
    for nb in arquivos(".ipynb"):
        cel = json.loads(ler(nb))["cells"]
        yield nb, "\n".join("".join(c["source"]) for c in cel if c["cell_type"] == "markdown")


def normalizar(sql):
    sql = re.sub(r"--[^\n]*", "", sql)
    return re.sub(r"\s+", " ", sql).strip().lower()


# 1. links e imagens -------------------------------------------------------
n_links = 0
for arq, texto in textos():
    sem_codigo = re.sub(r"```.*?```", "", texto, flags=re.S)
    for alvo in re.findall(r"\]\(([^)\s]+)", sem_codigo):
        if re.match(r"(https?|mailto):", alvo) or alvo.startswith("#"):
            continue
        caminho = unquote(alvo.split("#")[0])
        destino = os.path.normpath(os.path.join(RAIZ, os.path.dirname(arq), caminho))
        n_links += 1
        if not os.path.exists(destino):
            erros.append("%s: link quebrado -> %s" % (arq, alvo))

# 2 e 3. comandos make e tabelas ------------------------------------------
alvos_make = set(re.findall(r"^([a-zA-Z0-9_-]+):", ler("Makefile"), re.M))
sys.path.insert(0, RAIZ)
TABELAS = set(re.findall(r'^\s+"(\w+)":\s+\(\d', ler("liga/contrato.py"), re.M))
VALIDOS_T = TABELAS | {"legado", "fraude", "<tabela>"}
n_make = 0
for arq, texto in textos():
    for alvo, resto in re.findall(r"\bmake ([a-z][a-z0-9_-]*)([^\n`|]*)", texto):
        if alvo in ("command", "git"):     # "make: command not found", "apt install make git"
            continue
        n_make += 1
        if alvo not in alvos_make:
            erros.append("%s: `make %s` nao existe no Makefile" % (arq, alvo))
        for t in re.findall(r"\bt=([\w<>]+)", resto):
            if t not in VALIDOS_T:
                erros.append("%s: `make %s t=%s`: tabela desconhecida" % (arq, alvo, t))

# 4. o SQL do notebook e o do gabarito -------------------------------------
n_gab = 0
for fonte in sorted(arquivos(".txt")):
    if not fonte.startswith(os.path.join("scripts", "notebooks")):
        continue
    for gab in re.findall(r"^@gabarito (\S+)", ler(fonte), re.M):
        nb = os.path.join("notebooks", os.path.basename(fonte).replace(".txt", ".ipynb"))
        codigo = "\n".join("".join(c["source"]) for c in json.loads(ler(nb))["cells"]
                           if c["cell_type"] == "code")
        n_gab += 1
        if normalizar(ler(os.path.join("modelagem", "gabarito", gab))) not in normalizar(codigo):
            erros.append("%s: o SQL nao e igual a modelagem/gabarito/%s (rode scripts/gerar_notebooks.py)"
                         % (nb, gab))

# 5. notebooks em dia com as fontes ----------------------------------------
n_nb = 0
for fonte in sorted(arquivos(".txt")):
    if not fonte.startswith(os.path.join("scripts", "notebooks")):
        continue
    nb = os.path.join("notebooks", os.path.basename(fonte).replace(".txt", ".ipynb"))
    n_nb += 1
    if not os.path.exists(os.path.join(RAIZ, nb)):
        erros.append("%s: falta o notebook (rode scripts/gerar_notebooks.py)" % nb)
        continue
    md_fonte = [b.strip() for b in re.split(r"^=== \w+\n", ler(fonte), flags=re.M)[1:]]
    cel = ["".join(c["source"]).strip() for c in json.loads(ler(nb))["cells"]]
    for bloco in md_fonte:
        if bloco.startswith("@gabarito"):
            continue
        if bloco not in cel:
            erros.append("%s: desatualizado em relacao a %s (rode scripts/gerar_notebooks.py)" % (nb, fonte))
            break

print("links: %d   comandos make: %d   gabaritos: %d   notebooks: %d" % (n_links, n_make, n_gab, n_nb))
if erros:
    for e in erros:
        print("%s❌%s %s" % (R, F, e))
    print("%s%d problema(s).%s" % (R, len(erros), F))
    sys.exit(1)
print("%s✅ Documentação, notebooks e gabaritos consistentes.%s" % (V, F))
