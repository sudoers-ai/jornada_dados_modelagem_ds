# 3️⃣ A feature table do cliente

> ⬅️ Anterior: [2. O notebook herdado](../02_notebook_herdado/README.md) · [README principal](../../README.md) · Etapa 3 de 8

| | |
|---|---|
| **Notebook** | `notebooks/03_feature_table.ipynb` |
| **Você constrói** | `analytics.fs_cliente` |
| **Grão** | 1 linha por **cliente por dia** |
| **A prova** | `make conferir t=fs_cliente` |
| **Tempo** | 40 minutos |

## 🎯 Por que esta etapa existe

Na etapa 2, o notebook herdado usou o cliente **como ele é hoje** (a cidade atual, o
histórico inteiro de fraudes) para avaliar compras do passado. Em produção, nada disso
existe no momento da compra.

O antídoto é uma ***feature table point-in-time***: uma tabela que diz **como cada
cliente era no início de cada dia**, usando só o que aconteceu até o dia anterior. É o
coração do que o mercado chama de *feature store*. Qualquer modelo que pergunte "como era
este cliente no dia X?" recebe uma resposta sem futuro.

Três técnicas aparecem aqui e voltam no resto da trilha:

| Técnica | Para quê |
|---|---|
| **A grade** (todo cliente × todo dia) | ter uma linha por dia, inclusive os dias sem compra |
| **Janela "até ontem"** (`... AND 1 PRECEDING`) | nunca contar o próprio dia |
| ***As-of join*** com a `dim_pessoas` | pegar a versão do cliente que valia naquele dia |

## 📐 O contrato

As colunas e a regra de cada uma estão em
[`modelagem/dbml/analytics.dbml`](../../modelagem/dbml/analytics.dbml), na tabela
`fs_cliente`:

| Coluna | Regra |
|---|---|
| `id_pessoa`, `data` | a chave: um cliente num dia |
| `uf` | a UF do endereço que valia **naquele dia** |
| `dias_de_cadastro` | `data` menos o dia do cadastro |
| `qtd_pedidos_total` | pedidos feitos **antes** deste dia |
| `qtd_pedidos_30d` | pedidos nos 30 dias **anteriores** |
| `valor_medio_pedido` | média dos pedidos anteriores; nulo se nunca comprou |
| `dias_desde_ultimo_pedido` | nulo se nunca comprou |
| `qtd_dispositivos` | aparelhos diferentes usados **antes** deste dia |

## ▶️ Passo a passo

1. Abra **`03_feature_table.ipynb`** no JupyterLab.
2. Rode as seções 3.1 a 3.4 lendo o texto. Cada uma mostra uma técnica isolada, com um
   cliente só, para você ver a diferença entre o certo e o errado.
3. Na seção **3.5**, **leia o SQL inteiro antes de rodar**. Cada bloco do `WITH` é uma
   das técnicas acima, e os comentários dizem qual. Rode a célula: ela cria a
   `analytics.fs_cliente`.

   ```text
   ✅ Pronto (1.5s)
   ```

4. Rode a seção **3.6**, a prova.

## ✅ A prova

No notebook, `conferir("fs_cliente")`. Ou, no terminal:

```bash
make conferir t=fs_cliente
```

```text
Conferindo analytics.fs_cliente  (etapa 3)

  ✅ a tabela existe
  ✅ as 9 colunas do modelo estão lá, com os tipos certos
  ✅ grão: 1 linha por (id_pessoa, data), nenhuma repetida
  ✅ linhas: 90.500 (esperado 90.500)
  ✅ conteúdo: as 7 colunas batem com a referência, linha a linha

✅ analytics.fs_cliente conferida. Etapa 3 concluída!
```

A conferência compara a sua tabela com uma **referência** construída a partir do
contrato: mesma estrutura, mesmo grão e o mesmo valor em cada célula.

## 🧪 Experimente errar (recomendado)

O melhor jeito de entender a janela "até ontem" é quebrá-la de propósito.

1. Na célula da seção 3.5, ache a janela `ate_ontem` e troque o **primeiro**
   `1 PRECEDING` por `CURRENT ROW`.
2. Rode a célula e rode a conferência de novo. Ela vai apontar exatamente o que mudou:

   ```text
     ❌ qtd_pedidos_total: 4.888 linhas diferentes da referência
          exemplo: id_pessoa=1, data=2026-03-24 → sua tabela: 1, esperado: 0
          dica: conte só os dias ANTERIORES: a janela termina em 1 PRECEDING, e não em CURRENT ROW
     ❌ valor_medio_pedido: 4.888 linhas diferentes da referência
     ...
   ❌ 4 pendência(s) em analytics.fs_cliente. Corrija e confira de novo.
   ```

   Repare no exemplo: no dia 24 de março o cliente 1 comprou, e a sua tabela já "sabia"
   dessa compra no início do dia. É esse tipo de vazamento que fez o notebook herdado
   brilhar no notebook e falhar em produção.
3. Desfaça a troca (`Ctrl + Z` na célula), rode a célula e confira outra vez até voltar
   o ✅.

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `❌ O banco recusou o comando` | Leia a mensagem: é um erro de SQL. Se você editou a célula, desfaça com `Ctrl + Z`. Se não sabe o que mudou, restaure com `make gabarito t=fs_cliente` |
| `❌ ... linhas diferentes da referência` | A conferência diz a coluna, um exemplo e uma dica. Compare o exemplo com a regra do contrato |
| `linhas: 90.501 (esperado 90.500)` ou parecido | Erro de grão: algum `JOIN` multiplicou linhas. Confira o *as-of join* com a `dim_pessoas` (`<` em `dt_fim`, não `<=`) |
| Quero recomeçar do zero | `make refazer t=fs_cliente` apaga a sua tabela |
| Travei de vez | `make gabarito t=fs_cliente` aplica a resposta pronta |

## ✅ Antes de seguir

* [ ] Sei calcular o número de linhas esperado antes de escrever o SQL (500 × 181)
* [ ] Sei por que a janela termina em `1 PRECEDING`
* [ ] Sei fazer um *as-of join* com `dt_inicio` e `dt_fim`
* [ ] Fiz o "experimente errar" e vi a conferência apontar o erro
* [ ] `make conferir t=fs_cliente` deu ✅

---

# ➡️ Continue em [trilha/04_tabela_de_treino/README.md](../04_tabela_de_treino/README.md)
