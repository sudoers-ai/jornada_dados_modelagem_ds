# 2️⃣ O notebook herdado

> ⬅️ Anterior: [1. Conhecer o Data Warehouse](../01_conhecer_o_dw/README.md) · [README principal](../../README.md) · Etapa 2 de 8

| | |
|---|---|
| **Notebook** | `notebooks/02_notebook_herdado.ipynb` |
| **Você constrói** | nada novo: você **roda** o notebook antigo e o investiga |
| **A prova** | `make avaliar t=legado` |
| **Tempo** | 40 minutos |

## 🎯 Por que esta etapa existe

A pessoa que cuidava do antifraude antes de você deixou um notebook com **AUC de 0,99**.
Em produção, o modelo não pegava nem metade das fraudes prometidas.

Nesta etapa você reproduz o problema e encontra a causa. A lição central da disciplina
aparece aqui: **o algoritmo estava certo; a tabela estava errada.** Nenhum dos sete
erros que você vai achar se conserta trocando de modelo. Todos se consertam
**modelando a tabela de novo** — que é o que você faz nas etapas 3 e 4.

## ▶️ Passo a passo

### 1. Abra o notebook

No JupyterLab (http://localhost:8899), abra **`02_notebook_herdado.ipynb`**.

### 2. Parte A — rode o notebook como ele era

Rode as células da Parte A **sem alterar nada**. No fim, o notebook imprime o AUC:

```text
AUC no teste: 0.986
```

e salva o dataset dele em `legado.dataset_fraude`. É esse dataset que a prova avalia.

### 3. Parte B — veja o que aconteceu em produção

A célula `avaliar("legado")` treina o **mesmo** modelo de duas formas: como o notebook
fazia, e como a produção faz (treina no passado, dá nota aos pedidos de julho e agosto,
usando para cada coluna o valor que ela tinha **no momento da compra**).

```text
Avaliando legado.dataset_fraude
  modelo fixo: HistGradientBoostingClassifier, com as 9 colunas da tabela

                    AUC    PR-AUC   fraudes pegas revisando 10% dos pedidos
  no notebook      0.986   0.884      83%   (linhas sorteadas (train_test_split))
  em produção      0.627   0.317      36%   (pedidos de jul-ago, com o que se sabia na compra)

  ⚠️  3.45 linhas por pedido: o grão não é o pedido. ...
  ⚠️  colunas que NÃO tinham este valor no momento da compra:
       status                               100% dos pedidos mudam
       taxa_fraude_cliente                   47% dos pedidos mudam
       qtd_contas_dispositivo                 1% dos pedidos mudam

❌ O modelo perde 36 pontos de AUC entre o notebook e a produção.
   O notebook estava medindo o futuro, não o modelo.
```

> O ❌ aqui é o **resultado esperado**: é a prova de que o notebook mente. Não é um erro
> do seu ambiente.

### 4. Parte C — a investigação

Rode as células da Parte C, uma por uma. Cada uma isola um erro:

| # | Erro | Conceito |
|---|---|---|
| 1 | cada pedido virou mais de 3 linhas | **grão** |
| 2 | o mesmo pedido no treino e no teste | grão + **divisão temporal** |
| 3 | a cidade de hoje em compras do passado | **SCD tipo 2 / point-in-time** |
| 4 | `taxa_fraude_cliente` contém o rótulo | **vazamento de alvo** |
| 5 | `status` só existe depois da compra | **vazamento temporal** |
| 6 | `qtd_contas` é o total até a foto | **atributo calculado com o futuro** |
| 7 | fraudes ainda não descobertas | **maturação do rótulo** |

## ✅ A prova

No terminal:

```bash
make avaliar t=legado
```

A saída é a mesma da Parte B. E o placar marca a etapa:

```bash
make progresso
```

```text
  Etapa 2  O notebook herdado                 ✅ investigado
```

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `legado.dataset_fraude não existe` | Você não rodou a última célula da Parte A (a que salva o dataset). Rode-a |
| `NameError: name 'df' is not defined` | Você pulou células. Rode desde o início: **Run → Run All Cells** |
| A célula do `avaliar` demora | Ela treina dois modelos: leva alguns segundos. Espere o `[*]` virar número |

## ✅ Antes de seguir

* [ ] Rodei a Parte A e vi o AUC de ~0,99
* [ ] Rodei `avaliar("legado")` e vi a queda em produção
* [ ] Sei explicar cada um dos sete erros com uma frase
* [ ] `make progresso` mostra a etapa 2 como ✅ investigado

---

# ➡️ Continue em [trilha/03_feature_table/README.md](../03_feature_table/README.md)
