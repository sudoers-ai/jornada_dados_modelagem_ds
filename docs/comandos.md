# ⌨️ Comandos

> ⬅️ [README principal](../README.md)

Todo `make` deste repositório é um atalho para um ou mais comandos `docker`.
Esta página mostra o que está por trás de cada um: serve para entender o que
o atalho faz e para investigar quando algo dá errado. Rode sempre na **pasta
raiz** do repositório.

> O `make` é pré-requisito da trilha. Se você ainda não tem, veja os
> [pré-requisitos](../README.md#-pré-requisitos). No Windows, tudo desta
> página é digitado no terminal do Ubuntu (WSL): veja
> [Preparando o Windows](./windows.md).

## Ambiente

| `make` | Comando equivalente | Para quê |
|---|---|---|
| `make verificar` | `bash scripts/verificar.sh` | confere Docker, portas e memória antes de subir |
| `make subir` | `docker compose up -d --build` e `bash carga/carregar.sh` (no container) | sobe tudo e carrega o DW na primeira vez |
| `make status` | `docker compose ps -a` | os containers estão `healthy`? |
| `make derruba` | `docker compose down` | para tudo, **mantendo** dados e trabalho |
| `make limpar` | `docker compose down -v` | para tudo e **apaga o banco** (os notebooks ficam) |
| `make logs s=jupyter` | `docker compose logs -f jupyter` | segue os logs de um serviço (`Ctrl + C` sai) |
| `make consertar` | `docker compose up -d --force-recreate` | recria os containers sem apagar dados |
| `make diagnostico` | `bash scripts/diagnostico.sh` | relatório para mandar ao instrutor |
| `make carregar` | `bash carga/carregar.sh` (no container) | carrega o DW se ainda não estiver carregado |
| `make carregar args=--limpar` | o mesmo, apagando tudo antes | volta o banco ao estado inicial, **apagando as suas tabelas** |

## Trabalho

| `make` | Comando equivalente | Para quê |
|---|---|---|
| `make jupyter` | — | mostra o endereço do JupyterLab |
| `make psql` | `docker exec -it modelagem_ds_postgres psql -U sudoers -d liga_sudoers_dw` | SQL direto no DW (saia com `\q`) |
| `make sql f=arquivo.sql` | `docker compose exec jupyter psql -f arquivo.sql` | roda um arquivo `.sql` no DW |

## Provas

| `make` | Equivalente no notebook | Para quê |
|---|---|---|
| `make progresso` | `progresso()` | o seu placar |
| `make conferir` | — | confere todas as suas tabelas |
| `make conferir t=fs_cliente` | `conferir("fs_cliente")` | confere uma tabela contra o contrato |
| `make avaliar t=legado` | `avaliar("legado")` | o notebook herdado: notebook × produção |
| `make avaliar t=fraude` | `avaliar("fraude")` | a sua tabela de treino: notebook × produção |
| `make gabarito t=fs_cliente` | — | aplica a resposta pronta de uma tabela |
| `make refazer t=fs_cliente` | — | apaga uma tabela sua para refazer do zero |

As tabelas, na ordem da trilha: `fs_cliente`, `ds_pedido_fraude`,
`ds_cliente_mes`, `ds_peso_dia`, `ds_entrega`.

## Dentro do notebook

A primeira célula de todo notebook importa as ferramentas:

```python
from liga import sql, executar, conferir, avaliar, progresso
```

| Função | O que faz |
|---|---|
| `sql("SELECT ...")` | roda uma consulta e devolve um *DataFrame* do pandas |
| `executar("CREATE TABLE ...")` | roda comandos que não devolvem linhas (cria tabelas, por exemplo) e diz ✅ ou ❌ |
| `conferir("tabela")` | a mesma conferência do `make conferir` |
| `avaliar("legado")` / `avaliar("fraude")` | a mesma avaliação do `make avaliar` |
| `progresso()` | o placar |

## Manutenção (para quem mantém o repositório)

| `make` | Para quê |
|---|---|
| `make testar-trilha` | executa os sete notebooks em ordem, num banco limpo, e confere tudo |
