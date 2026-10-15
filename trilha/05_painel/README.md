# 5️⃣ O painel cliente × mês

> ⬅️ Anterior: [4. A tabela de treino do antifraude](../04_tabela_de_treino/README.md) · [README principal](../../README.md) · Etapa 5 de 8

| | |
|---|---|
| **Notebook** | `notebooks/05_painel.ipynb` |
| **Você constrói** | `analytics.ds_cliente_mes` |
| **Grão** | 1 linha por **cliente por mês completo**, inclusive os meses sem compra |
| **A prova** | `make conferir t=ds_cliente_mes` |
| **Tempo** | 30 minutos |

## 🎯 Por que esta etapa existe

O time de CRM quer prever **quem vai comprar no mês que vem**, para agir antes de o
cliente sumir. Para isso precisa de um **painel** (*panel data*): cada cliente, em cada
mês, com o rótulo `comprou_mes_seguinte`.

A armadilha desta etapa é a mais comum de todas: **o mês em que o cliente não comprou
também é um dado.** Um `GROUP BY cliente, mês` só cria linha para os meses **com**
compra. O cliente que sumiu — exatamente quem o CRM quer encontrar — desaparece da
tabela.

| Problema da tabela ingênua | Solução |
|---|---|
| faltam os meses sem compra | a **grade**: todo cliente × todo mês, com `LEFT JOIN` e `0` |
| o `LEAD` pega o próximo mês **com compra**, não o mês seguinte | com a grade, a próxima linha é o próximo mês do calendário |
| março e setembro estão pela metade | só **meses completos** (abril a agosto) |
| o último mês não tem "seguinte" | rótulo **nulo** em agosto |

## ▶️ Passo a passo

1. Abra **`05_painel.ipynb`** no JupyterLab.
2. Rode a seção 5.1 e veja o cliente 10 na tabela ingênua: ele comprou em maio e só
   voltou em agosto. Para a tabela ingênua, o "mês seguinte" de maio é agosto.
3. Rode as seções 5.2 e 5.3. Antes de construir, a 5.3 calcula o tamanho esperado:
   500 clientes × 5 meses = **2.500 linhas**.
4. Na seção **5.4**, leia o SQL (repare nas duas regras de negócio: cancelados e
   devolvidos não contam; a janela de 3 meses só olha para trás) e rode.
5. Rode a conferência e a seção 5.5, que usa o painel.

## ✅ A prova

```bash
make conferir t=ds_cliente_mes
```

```text
  ✅ a tabela existe
  ✅ as 7 colunas do modelo estão lá, com os tipos certos
  ✅ grão: 1 linha por (id_pessoa, mes), nenhuma repetida
  ✅ linhas: 2.500 (esperado 2.500)
  ✅ conteúdo: as 5 colunas batem com a referência, linha a linha

✅ analytics.ds_cliente_mes conferida. Etapa 5 concluída!
```

## 🆘 Se deu errado

| O que apareceu | O que fazer |
|---|---|
| `linhas:` abaixo de 2.500 | Faltam os meses sem compra: a tabela partiu das compras, e não da grade |
| `linhas: 3.000` ou mais | Entraram março ou setembro, que estão incompletos |
| `❌ comprou_mes_seguinte` | O `LEAD` tem que rodar **na grade completa**; e agosto fica nulo |
| `❌ qtd_pedidos` | Cancelados e devolvidos não contam; mês sem compra é `0`, não nulo |
| Travei | `make gabarito t=ds_cliente_mes` |

## ✅ Antes de seguir

* [ ] Vi a tabela ingênua perder os meses sem compra
* [ ] Sei por que o `LEAD` só funciona com a grade completa
* [ ] Sei por que se usam só meses completos
* [ ] `make conferir t=ds_cliente_mes` deu ✅

---

# ➡️ Continue em [trilha/06_serie_temporal/README.md](../06_serie_temporal/README.md)
