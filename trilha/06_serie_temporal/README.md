# 6️⃣ A série temporal do peso transportado

> ⬅️ Anterior: [5. O painel cliente × mês](../05_painel/README.md) · [README principal](../../README.md) · Etapa 6 de 8

| | |
|---|---|
| **Notebook** | `notebooks/06_serie_temporal.ipynb` |
| **Você constrói** | `analytics.ds_peso_dia` |
| **Grão** | 1 linha por **dia por transportadora**, inclusive os dias sem caminhão |
| **A prova** | `make conferir t=ds_peso_dia` |
| **Tempo** | 30 minutos |

## 🎯 Por que esta etapa existe

A logística quer **prever o peso** que cada transportadora vai levar, para negociar o
frete. Previsão é série temporal, e série temporal tem uma regra que o SQL ingênuo quebra
sem avisar: **todo dia precisa existir**.

A `fato_peso_diario` do DW só tem linha nos dias **com caminhão**. Para a fato isso está
certo: ela registra o que aconteceu. Para uma série temporal é um buraco, e o buraco
quebra as features mais comuns:

| Feature | Com buracos | Com a grade |
|---|---|---|
| `LAG(peso, 7)` | volta 7 **linhas**: pode ser duas semanas atrás | volta 7 **dias** |
| média dos últimos 7 | mistura dias de semanas diferentes | 7 dias de verdade |

A solução é a mesma das etapas 3 e 5: **primeiro a grade** (`dim_tempo` ×
`dim_transportadora`), depois `LEFT JOIN` dos dados, com **zero** onde não houve
caminhão.

## ▶️ Passo a passo

1. Abra **`06_serie_temporal.ipynb`** no JupyterLab.
2. Rode a seção 6.1: a série ingênua tem **490** linhas; a grade completa precisa de
   **895** (179 dias × 5 transportadoras).
3. Rode a 6.2 e veja, na coluna `dias_de_distancia_de_verdade`, o `LAG(7)` voltando 12,
   14, 16 dias.
4. Leia a 6.3, rode a **6.4** (constrói a tabela) e a conferência.
5. Rode a 6.5: a mesma série no formato **longo** e no **largo** (`pivot`), e o gráfico
   semanal.

## ✅ A prova

```bash
make conferir t=ds_peso_dia
```

```text
  ✅ a tabela existe
  ✅ as 10 colunas do modelo estão lá, com os tipos certos
  ✅ grão: 1 linha por (data, id_transportadora), nenhuma repetida
  ✅ linhas: 895 (esperado 895)
  ✅ conteúdo: as 8 colunas batem com a referência, linha a linha

✅ analytics.ds_peso_dia conferida. Etapa 6 concluída!
```

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `linhas: 490 (esperado 895)` | A tabela partiu da `fato_peso_diario`: faltam os dias sem caminhão. Parta da grade |
| `❌ peso_kg_7_dias_antes` | Com a grade, `LAG(peso, 7)` **por transportadora** (`PARTITION BY`) |
| `❌ media_7_dias_anteriores` | `ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING`: sem o próprio dia |
| `❌ peso_kg` ou `qtd_pedidos` com nulos | Dia sem caminhão é `0`, não nulo: use `COALESCE` |
| Travei | `make gabarito t=ds_peso_dia` |

## ✅ Antes de seguir

* [ ] Vi o `LAG(7)` voltar mais de 7 dias na série com buracos
* [ ] Sei montar a grade dia × transportadora
* [ ] Sei a diferença entre formato longo e largo, e quando usar cada um
* [ ] `make conferir t=ds_peso_dia` deu ✅

---

# ➡️ Continue em [trilha/07_rotulo_por_regra/README.md](../07_rotulo_por_regra/README.md)
