#!/usr/bin/env bash
# ==========================================================================
# Confere o terreno ANTES de subir a stack: Docker, Compose v2, portas e
# memoria. A maior parte dos problemas de aula e porta ocupada - e e bem
# mais facil corrigir antes do que depois.
# ==========================================================================
set -uo pipefail
V="\033[92m"; A="\033[93m"; R="\033[91m"; N="\033[1m"; F="\033[0m"
[ -f .env ] && set -a && . ./.env && set +a

PORTA_POSTGRES="${PORTA_POSTGRES:-5450}"
PORTA_JUPYTER="${PORTA_JUPYTER:-8899}"
erros=0

ok()    { echo -e "  ${V}✅${F} $1"; }
aviso() { echo -e "  ${A}⚠️ ${F} $1"; }
erro()  { echo -e "  ${R}❌${F} $1"; erros=$((erros + 1)); }

echo
echo -e "${N}Conferindo o ambiente${F}"
echo

if ! command -v docker >/dev/null 2>&1; then
  erro "Docker não encontrado. Instale: https://docs.docker.com/get-docker/"
  echo; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  erro "O Docker está instalado, mas não responde. Ele está aberto? (no Linux: sudo systemctl start docker)"
  echo; exit 1
fi
ok "Docker respondendo ($(docker --version | awk '{print $3}' | tr -d ','))"

if docker compose version >/dev/null 2>&1; then
  ok "Docker Compose v2 ($(docker compose version --short 2>/dev/null))"
else
  erro "Falta o Docker Compose v2. O comando é 'docker compose' (com espaço), não 'docker-compose'."
  echo "       Linux: sudo apt install docker-compose-plugin"
fi

porta_ocupada() {
  local p="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE "[:.]${p}\$"
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1
  else
    (exec 3<>"/dev/tcp/127.0.0.1/$p") >/dev/null 2>&1
  fi
}

conferir_porta() {
  local nome="$1" porta="$2" container="$3" variavel="$4"
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$container"; then
    ok "porta $porta ($nome) em uso pelo próprio $container — já está no ar"
  elif porta_ocupada "$porta"; then
    erro "porta $porta ($nome) está ocupada por outro programa."
    echo "       Abra o arquivo .env e troque $variavel=$porta por outra, ex.: $variavel=$((porta + 100))"
  else
    ok "porta $porta livre ($nome)"
  fi
}
conferir_porta "PostgreSQL (o Data Warehouse)" "$PORTA_POSTGRES" modelagem_ds_postgres PORTA_POSTGRES
conferir_porta "JupyterLab"                   "$PORTA_JUPYTER"  modelagem_ds_jupyter  PORTA_JUPYTER

mem_kb=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0)
mem_gb=$(( mem_kb / 1024 / 1024 / 1024 ))
if [ "$mem_gb" -ge 4 ]; then
  ok "memória disponível para o Docker: ${mem_gb} GB"
elif [ "$mem_gb" -ge 2 ]; then
  aviso "memória disponível para o Docker: ${mem_gb} GB. Funciona, mas feche outros programas pesados."
else
  aviso "memória para o Docker abaixo de 2 GB. Aumente em Docker Desktop > Settings > Resources."
fi

echo
if [ "$erros" -gt 0 ]; then
  echo -e "${R}${erros} problema(s) acima.${F} Corrija e rode ${N}make verificar${F} de novo."
  echo "Dúvidas: docs/faq.md"
  echo; exit 1
fi
echo -e "${V}Tudo certo.${F} Próximo passo: ${N}make subir${F}"
echo
