# ==========================================================================
# Liga Sudoers - Modelagem de Dados para Cientistas de Dados - atalhos
#
#   make ajuda      lista tudo
#
# Todo `make` corresponde a comandos `docker` (veja docs/comandos.md).
# ==========================================================================
.DEFAULT_GOAL := ajuda
SHELL := /bin/bash
DC    := docker compose
NO_JUPYTER := $(DC) exec -T jupyter
PSQL  := psql -v ON_ERROR_STOP=1 -U sudoers -d liga_sudoers_dw

# o container do Jupyter roda com o seu usuario (os notebooks salvos ficam seus)
export UID := $(shell id -u)
export GID := $(shell id -g)

$(shell [ -f .env ] || cp .env.example .env 2>/dev/null)
# as portas escolhidas no .env valem tambem para o verificar e para as mensagens
-include .env
export PORTA_POSTGRES PORTA_JUPYTER

.PHONY: ajuda verificar subir carregar status derruba limpar logs consertar diagnostico \
        jupyter psql sql conferir progresso avaliar gabarito refazer testar-trilha

ajuda:  ## mostra esta ajuda
	@echo ""
	@echo "  Liga Sudoers - Modelagem de Dados para Cientistas de Dados"
	@echo "  ---------------------------------------------------------------"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------- ambiente
verificar:   ## confere Docker, portas e memoria ANTES de subir
	@bash scripts/verificar.sh

subir:       ## sobe o banco e o JupyterLab, e carrega o DW na primeira vez
	$(DC) up -d --build
	@echo "aguardando os containers ficarem prontos..."
	@bash scripts/esperar.sh
	@$(NO_JUPYTER) bash carga/carregar.sh
	@echo ""
	@echo "  Tudo no ar. Abra o JupyterLab: http://localhost:$${PORTA_JUPYTER:-8899}"
	@echo "  e continue em trilha/01_conhecer_o_dw/README.md"
	@echo ""

carregar:    ## carrega o DW (args=--limpar apaga TUDO e carrega de novo)
	@bash scripts/esperar.sh
	@$(NO_JUPYTER) bash carga/carregar.sh $(args)

status:      ## mostra o estado dos containers
	@$(DC) ps -a --format 'table {{.Name}}\t{{.Service}}\t{{.Status}}'

derruba:     ## para os containers (MANTEM os dados e o seu trabalho)
	$(DC) down

limpar:      ## para tudo e APAGA o banco (os notebooks continuam na pasta)
	$(DC) down -v

logs:        ## segue os logs de um servico (make logs s=jupyter)
	$(DC) logs -f $(s)

consertar:   ## recria os containers (NAO apaga os dados)
	$(DC) up -d --force-recreate
	@bash scripts/esperar.sh

diagnostico: ## junta tudo que o instrutor precisa para te ajudar
	@bash scripts/diagnostico.sh

# --------------------------------------------------------------- trabalho
jupyter:     ## mostra o endereco do JupyterLab
	@echo "  http://localhost:$${PORTA_JUPYTER:-8899}"

psql:        ## abre o psql no Data Warehouse (saia com \q)
	@docker exec -it modelagem_ds_postgres $(PSQL)

sql:         ## roda um arquivo .sql no DW (make sql f=caminho.sql)
	@test -n "$(f)" || (echo "uso: make sql f=caminho/do/arquivo.sql" && exit 1)
	@$(NO_JUPYTER) psql -v ON_ERROR_STOP=1 -f $(f)

# ---------------------------------------------------------------- provas
conferir:    ## confere uma tabela sua contra o modelo (make conferir t=fs_cliente)
	@bash scripts/esperar.sh
	@$(NO_JUPYTER) python -m liga.conferir $(t)

progresso:   ## o seu placar: o que ja esta pronto na trilha
	@bash scripts/esperar.sh
	@$(NO_JUPYTER) python -m liga.progresso

avaliar:     ## treina um modelo na tabela e compara notebook x producao (t=legado|fraude)
	@bash scripts/esperar.sh
	@$(NO_JUPYTER) python -m liga.avaliar $(t)

gabarito:    ## aplica a RESPOSTA de uma tabela (make gabarito t=fs_cliente)
	@test -n "$(t)" || (echo "uso: make gabarito t=<tabela>" && exit 1)
	@$(NO_JUPYTER) python -m liga.gabarito $(t)

refazer:     ## apaga uma tabela sua para refazer do zero (make refazer t=fs_cliente)
	@test -n "$(t)" || (echo "uso: make refazer t=<tabela>" && exit 1)
	@$(NO_JUPYTER) psql -q -c "DROP TABLE IF EXISTS analytics.$(t) CASCADE" && echo "analytics.$(t) apagada."

testar-trilha: ## (manutencao) executa todos os notebooks, em ordem, e confere
	@$(NO_JUPYTER) python tests/testar_trilha.py $(args)
