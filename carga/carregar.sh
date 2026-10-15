#!/usr/bin/env bash
# ==========================================================================
# Carrega o Data Warehouse que voce vai usar na disciplina.
#
#   bash carga/carregar.sh            carrega (se ainda nao estiver carregado)
#   bash carga/carregar.sh --limpar   apaga TUDO (inclusive o seu schema
#                                     analytics) e carrega de novo
#
# Voce nao precisa ler este arquivo: e o mesmo processo da Parte 3
# (transacional -> ETL -> star schema), feito de uma vez, sem pausa.
# Roda dentro do container `jupyter` (o `make carregar` cuida disso).
# ==========================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
V="\033[92m"; C="\033[90m"; F="\033[0m"

export PGHOST="${PGHOST:-postgres}" PGUSER=sudoers PGPASSWORD=password
export PGOPTIONS="--client-min-messages=warning"
OLTP="psql -v ON_ERROR_STOP=1 -q -d liga_sudoers"
DW="psql -v ON_ERROR_STOP=1 -q -d liga_sudoers_dw"

ja=$($DW -tAc "SELECT count(*) FROM information_schema.tables WHERE table_name = 'fato_ciclo_pedido'")
if [ "${1:-}" != "--limpar" ] && [ "$ja" != "0" ] \
   && [ "$($DW -tAc 'SELECT count(*) > 0 FROM fato_ciclo_pedido')" = "t" ]; then
  echo -e "${V}✅ O Data Warehouse já está carregado.${F} Nada foi alterado."
  echo "   Para apagar tudo e carregar de novo: make carregar args=--limpar"
  exit 0
fi

echo "Carregando o Data Warehouse da Liga Sudoers (leva menos de 1 minuto)..."
$OLTP -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
$DW   -c "DROP SCHEMA IF EXISTS analytics CASCADE; DROP SCHEMA IF EXISTS referencia CASCADE;
          DROP SCHEMA IF EXISTS legado CASCADE; DROP SCHEMA IF EXISTS stg CASCADE;
          DROP SCHEMA IF EXISTS oltp CASCADE; DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo -e "  1/4 transacional: modelo e cadastro"
$OLTP -f carga/ddl/01_oltp_schema.sql
$OLTP -f carga/ddl/02_oltp_dados_base.sql > /dev/null
$OLTP -f carga/ddl/03_oltp_evolucao.sql

echo -e "  2/4 transacional: 180 dias de pedidos"
python carga/carregar_historico.py

echo -e "  3/4 dimensional: o star schema"
$DW -f carga/ddl/04_dw_schema.sql
$DW -f carga/ddl/05_dw_evolucao.sql

echo -e "  4/4 ETL: do transacional para o dimensional"
for f in carga/etl/*.sql; do
  echo -e "     ${C}$(basename "$f")${F}"
  $DW -f "$f" > /dev/null
done
$DW -c "DROP SCHEMA IF EXISTS oltp CASCADE;"
$DW -c "CREATE SCHEMA analytics; CREATE SCHEMA legado; CREATE SCHEMA referencia;"

echo
$DW -c "SELECT (SELECT count(*) FROM fato_pedidos)      AS itens_vendidos,
               (SELECT count(*) FROM fato_ciclo_pedido) AS pedidos,
               (SELECT count(DISTINCT id) FROM dim_pessoas) AS clientes,
               (SELECT min(dt_venda)::date FROM fato_pedidos) AS de,
               (SELECT max(dt_venda)::date FROM fato_pedidos) AS ate;"
echo -e "${V}✅ Data Warehouse carregado.${F}"
