#!/usr/bin/env bash
# ==========================================================================
# Junta, num relatorio so, tudo que o instrutor precisa para te ajudar.
# Copie a saida inteira e mande para ele.
# ==========================================================================
set -uo pipefail
linha() { echo; echo "==================== $1 ===================="; }

linha "sistema"
uname -a
docker --version 2>&1
docker compose version 2>&1
make --version 2>&1 | head -1
echo "memoria do Docker: $(( $(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0) / 1024 / 1024 )) MB"
echo "pasta: $(pwd)"

linha "arquivo .env"
[ -f .env ] && cat .env || echo "(sem .env - usando os padroes)"

linha "containers"
docker ps -a --filter "name=modelagem_ds_" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

linha "tabelas do DW e as suas (schema analytics)"
docker exec modelagem_ds_postgres psql -U sudoers -d liga_sudoers_dw -c '\dt public.*' -c '\dt analytics.*' 2>&1 | head -40

linha "progresso"
docker compose exec -T jupyter python -m liga.progresso 2>&1 | tail -30

for c in modelagem_ds_postgres modelagem_ds_jupyter; do
  linha "ultimas linhas do log: $c"
  docker logs --tail 15 "$c" 2>&1
done
