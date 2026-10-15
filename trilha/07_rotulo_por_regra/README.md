# 7️⃣ O rótulo definido por regra: a entrega atrasou?

> ⬅️ Anterior: [6. A série temporal do peso transportado](../06_serie_temporal/README.md) · [README principal](../../README.md) · Etapa 7 de 8

| | |
|---|---|
| **Notebook** | `notebooks/07_rotulo_por_regra.ipynb` |
| **Você constrói** | `analytics.ds_entrega` |
| **Grão** | 1 linha por **pedido embarcado** num transporte |
| **A prova** | `make conferir t=ds_entrega` |
| **Tempo** | 30 minutos |

## 🎯 Por que esta etapa existe

Na fraude, o rótulo vinha pronto: alguém confirmou. Muitas vezes ele **não existe** no
banco, e é você que o define a partir de uma regra de negócio. "A entrega atrasou" é um
desses: `atrasou` = foi entregue **depois** da data prevista.

Parece simples, e tem duas armadilhas:

| Armadilha | O que acontece | A solução |
|---|---|---|
| **A coluna pronta** | `fato_entregas.is_atrasada` foi calculada com a hora em que o ETL rodou: para quem ainda está na estrada, ela muda a cada carga | o rótulo só existe para quem **já chegou** |
| **A censura** | dos caminhões recentes, só os rápidos já chegaram: a taxa de atraso parece menor do que é | só julgar saídas com mais de **10 dias**; as recentes ficam com rótulo **nulo** |

E uma feature com o cuidado de sempre: a taxa de atraso da transportadora calculada só
com entregas **concluídas antes** de o caminhão sair.

## ▶️ Passo a passo

1. Abra **`07_rotulo_por_regra.ipynb`** no JupyterLab.
2. Rode a seção 7.1 e veja a `is_atrasada` preenchida para entregas que nem chegaram.
3. Rode a 7.2: compare a taxa de atraso dos caminhões que saíram nos últimos 10 dias com a
   dos mais antigos, e a coluna dos que **já passaram do prazo e ainda estão na estrada**.
4. Leia a 7.3, rode a **7.4** (constrói a tabela) e a conferência.
5. Rode a 7.5: com o rótulo honesto, qual transportadora mais atrasa?

## ✅ A prova

```bash
make conferir t=ds_entrega
```

```text
  ✅ a tabela existe
  ✅ as 13 colunas do modelo estão lá, com os tipos certos
  ✅ grão: 1 linha por (id_transporte, id_pedido), nenhuma repetida
  ✅ linhas: 4.599 (esperado 4.599)
  ✅ conteúdo: as 11 colunas batem com a referência, linha a linha

✅ analytics.ds_entrega conferida. Etapa 7 concluída!
```

E o placar completo:

```bash
make progresso
```

```text
  ██████  6 de 6 etapas com prova concluídas
  🏁 Trilha completa. Siga para os desafios: desafios/desafios.md
```

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `❌ atrasou` | Nulo para saídas dos últimos 10 dias antes da foto. Nos outros, compare `dt_entrega` com `dt_entrega_prevista` (não use `is_atrasada`) |
| `❌ taxa_atraso_transportadora` | Só entregas com `dt_entrega` **antes** do `dt_saida` deste caminhão |
| `❌ particao` | Veja a regra da partição no contrato (`analytics.dbml`) |
| Travei | `make gabarito t=ds_entrega` |

## ✅ Antes de seguir

* [ ] Sei por que `is_atrasada` não serve como rótulo
* [ ] Sei explicar censura com o exemplo dos caminhões recentes
* [ ] Sei por que a taxa da transportadora só olha entregas anteriores à saída
* [ ] `make conferir t=ds_entrega` deu ✅
* [ ] `make progresso` mostra 6 de 6

---

🏁 **Fim da trilha guiada.**

# ➡️ Continue em [desafios/desafios.md](../../desafios/desafios.md)
