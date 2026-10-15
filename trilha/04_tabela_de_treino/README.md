# 4️⃣ A tabela de treino do antifraude

> ⬅️ Anterior: [3. A feature table do cliente](../03_feature_table/README.md) · [README principal](../../README.md) · Etapa 4 de 8

| | |
|---|---|
| **Notebook** | `notebooks/04_tabela_de_treino.ipynb` |
| **Você constrói** | `analytics.ds_pedido_fraude` |
| **Grão** | 1 linha por **pedido** |
| **Depende de** | `analytics.fs_cliente` (etapa 3) |
| **A prova** | `make conferir t=ds_pedido_fraude` e `make avaliar t=fraude` |
| **Tempo** | 50 minutos |

## 🎯 Por que esta etapa existe

É a etapa central da disciplina. Você refaz, do jeito certo, a tabela que o notebook
herdado usava, e corrige os sete erros da etapa 2 — **sem mexer no modelo**.

| | |
|---|---|
| **Grão** | um pedido: os itens são **agregados antes** de qualquer junção |
| **Regra de ouro** | toda feature usa só o que se sabia **no momento da compra** |
| **Rótulo** | `is_fraude`, só quando já está **maduro** (nulo nos últimos 7 dias) |
| **Divisão** | coluna `particao`, **temporal**: `treino` no passado, `teste` depois, `sem_rotulo` no fim |

As 22 colunas e a regra de cada uma estão no contrato,
[`modelagem/dbml/analytics.dbml`](../../modelagem/dbml/analytics.dbml), na tabela
`ds_pedido_fraude`.

## ▶️ Passo a passo

1. Confira que a etapa 3 está pronta: `make conferir t=fs_cliente` tem que dar ✅. A
   tabela de treino lê as features do cliente de lá.
2. Abra **`04_tabela_de_treino.ipynb`** no JupyterLab.
3. Rode as seções 4.1 a 4.4 lendo o texto. Na 4.3, veja o aparelho de um anel de fraude
   começar com `0` outras contas e crescer compra a compra — o notebook herdado dava o
   número final desde a primeira compra.
4. Na seção **4.5**, leia o SQL e rode. Ela cria a `analytics.ds_pedido_fraude`.
5. Rode a **4.6** (a conferência) e a **4.7** (a prova de fogo).

## ✅ A prova

```bash
make conferir t=ds_pedido_fraude
```

```text
  ✅ a tabela existe
  ✅ as 22 colunas do modelo estão lá, com os tipos certos
  ✅ grão: 1 linha por (id_pedido), nenhuma repetida
  ✅ linhas: 5.000 (esperado 5.000)
  ✅ conteúdo: as 21 colunas batem com a referência, linha a linha

✅ analytics.ds_pedido_fraude conferida. Etapa 4 concluída!
```

### 🔥 A prova de fogo

O mesmo teste que derrubou o notebook herdado, agora com a sua tabela:

```bash
make avaliar t=fraude
```

```text
                    AUC    PR-AUC   fraudes pegas revisando 10% dos pedidos
  no notebook      0.942   0.736      72%   (divisão da própria tabela (coluna particao))
  em produção      0.942   0.736      72%   (pedidos de jul-ago, com o que se sabia na compra)

✅ Notebook e produção concordam. A tabela só usa o que existia no momento da compra.
```

Coloque lado a lado com o herdado:

| Tabela | AUC no notebook | AUC em produção | Fraudes pegas em produção |
|---|---|---|---|
| `legado.dataset_fraude` | 0,986 | **0,627** | 36% |
| `analytics.ds_pedido_fraude` | 0,942 | **0,942** | 72% |

O seu modelo parece **pior** no notebook e é **muito melhor** em produção. Mais
importante: o número que você vê é o número que a empresa vai ter. É isso que uma boa
modelagem entrega a um cientista de dados: **um número em que se pode confiar**.

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `relation "analytics.fs_cliente" does not exist` | A etapa 3 não foi feita. Volte a ela, ou rode `make gabarito t=fs_cliente` |
| `❌ is_fraude: ... linhas diferentes` | O rótulo dos últimos 7 dias tem que ser **nulo**, não `false` |
| `❌ qtd_outras_contas_no_dispositivo` | Conte só as **outras** pessoas, e só as que usaram o aparelho **antes** desta compra |
| `linhas: 15.000 (esperado 5.000)` ou parecido | Os itens não foram agregados antes da junção (grão de item) |
| O `avaliar("fraude")` dá números diferentes dos acima | Rode `make conferir t=ds_pedido_fraude`. Se a conferência der ✅, os números batem |
| Travei | `make gabarito t=ds_pedido_fraude` |

## ✅ Antes de seguir

* [ ] Sei por que se agrega a `fato_pedidos` **antes** de juntar
* [ ] Sei a diferença entre rótulo **nulo** e rótulo `false`
* [ ] Sei por que a divisão é temporal e não sorteada
* [ ] `make conferir t=ds_pedido_fraude` deu ✅
* [ ] Rodei `make avaliar t=fraude` e comparei com o legado

---

# ➡️ Continue em [trilha/05_painel/README.md](../05_painel/README.md)
