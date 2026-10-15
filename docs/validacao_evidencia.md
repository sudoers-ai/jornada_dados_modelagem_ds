# 🔎 Guia de validação por evidências

> ⬅️ [README principal](../README.md)

"Rodou sem erro" não é evidência. Evidência é um **resultado que você
consegue mostrar** e que só existe se a etapa deu certo. Este guia diz, para
cada etapa, qual é esse resultado e como obtê-lo.

Regra geral: nesta disciplina toda etapa tem um **comando de prova** que
termina com ✅ ou diz o que falta.

| Etapa | Comando de prova | Evidência de sucesso |
|---|---|---|
| 0 | `make status` | 2 containers `healthy` |
| 2 | `make avaliar t=legado` | AUC 0,986 no notebook e 0,627 em produção |
| 3 | `make conferir t=fs_cliente` | `✅ analytics.fs_cliente conferida` |
| 4 | `make conferir t=ds_pedido_fraude` | `✅ analytics.ds_pedido_fraude conferida` |
| 4 | `make avaliar t=fraude` | `✅ Notebook e produção concordam` |
| 5 | `make conferir t=ds_cliente_mes` | `✅ analytics.ds_cliente_mes conferida` |
| 6 | `make conferir t=ds_peso_dia` | `✅ analytics.ds_peso_dia conferida` |
| 7 | `make conferir t=ds_entrega` | `✅ analytics.ds_entrega conferida` |
| fim | `make progresso` | `6 de 6 etapas com prova concluídas` |

---

## 0) Ambiente

```bash
make status
```

Os dois containers com `(healthy)`. Evidência complementar:
http://localhost:8899 abre o JupyterLab na pasta `notebooks`.

## 1) O DW

Não há prova automática: a evidência é você conseguir responder, sem olhar,
qual o grão de cada fato e por que a `dim_pessoas` tem 578 linhas para 500
pessoas.

## 2) O notebook herdado

```bash
make avaliar t=legado
```

A queda de 36 pontos de AUC entre "no notebook" e "em produção", e as três
colunas listadas como "colunas que NÃO tinham este valor no momento da
compra". O ❌ no fim é o resultado esperado.

## 3) a 7) As tabelas

```bash
make conferir t=<tabela>
```

Cinco linhas com ✅: a tabela existe, as colunas e os tipos estão certos, o
grão não tem repetição, o número de linhas bate e o conteúdo bate **linha a
linha** com a referência. A referência é construída a partir do contrato
(`modelagem/dbml/analytics.dbml`) toda vez que você confere.

| Tabela | Linhas |
|---|---|
| `fs_cliente` | 90.500 |
| `ds_pedido_fraude` | 5.000 |
| `ds_cliente_mes` | 2.500 |
| `ds_peso_dia` | 895 |
| `ds_entrega` | 4.599 |

## 4) A prova de fogo

```bash
make avaliar t=fraude
```

As duas linhas, "no notebook" e "em produção", com o **mesmo** AUC (0,942) e a
mensagem `✅ Notebook e produção concordam`.

---

## Para entregar

Um bom relatório de evidências tem, para cada etapa:

1. o comando de prova e a saída dele;
2. uma frase dizendo **o que aquela saída prova**;
3. (opcional) um *print* do notebook.

A frase do item 2 é o que diferencia quem executou de quem entendeu. Na
etapa 4, por exemplo: "o AUC do notebook é igual ao de produção porque a
tabela só usa o que existia no momento da compra".
