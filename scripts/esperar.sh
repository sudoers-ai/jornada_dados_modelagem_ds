#!/usr/bin/env bash
# ==========================================================================
# Espera os containers ficarem saudaveis. Evita o erro classico de rodar um
# comando com o banco ainda subindo.
# ==========================================================================
set -uo pipefail
V="\033[92m"; A="\033[93m"; R="\033[91m"; C="\033[90m"; F="\033[0m"

ALVOS=(modelagem_ds_postgres modelagem_ds_jupyter)
LIMITE=300

estado() {
  local e
  e=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$1" 2>/dev/null) || e=""
  echo "${e:-ausente}"
}

for c in "${ALVOS[@]}"; do
  inicio=$(date +%s)
  avisou=0
  while true; do
    e=$(estado "$c")
    if [ "$e" = "healthy" ]; then
      [ "$avisou" = 1 ] && echo -e "\r  ${V}✅${F} $c pronto                              "
      break
    fi
    if [ "$e" = "ausente" ]; then
      echo -e "  ${R}❌${F} o container $c não existe. Rode: make subir"
      exit 1
    fi
    agora=$(date +%s)
    if [ $((agora - inicio)) -ge "$LIMITE" ]; then
      echo -e "\n  ${R}❌${F} $c não ficou pronto em ${LIMITE}s (estado: $e)."
      echo "     Veja o motivo com: docker logs $c | tail -30"
      echo "     E consulte docs/faq.md"
      exit 1
    fi
    avisou=1
    echo -ne "\r  ${A}⏳${F} esperando $c ... ${C}$((agora - inicio))s${F}   "
    sleep 2
  done
done
