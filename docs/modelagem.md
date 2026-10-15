# 📐 Do star schema à tabela de treino

> ⬅️ [README principal](../README.md)

Este é o texto que explica o **porquê** de cada etapa da trilha. Leia antes,
durante ou depois — mas leia. Os notebooks mostram o *como*; aqui está a ideia
que liga tudo.

---

## 1. Duas perguntas diferentes

Um Data Warehouse responde perguntas sobre o **passado, olhando de hoje**:
"quanto vendemos em julho?", "qual transportadora atrasa mais?". Para isso
ele guarda os fatos com o contexto mais completo possível, e é bom que guarde:
quanto mais se sabe, melhor a resposta.

Um modelo de machine learning responde uma pergunta sobre o **futuro, olhando
do momento da decisão**: "este pedido, que acabou de chegar, é fraude?". No
momento da decisão, muita coisa que o DW sabe **ainda não aconteceu**.

> **Uma tabela para ciência de dados é uma promessa sobre o tempo:** cada
> linha diz o que se sabia **naquele momento** — nem mais, nem menos.

Quase todos os erros desta disciplina são quebras dessa promessa.

## 2. O grão

O grão é a resposta para "o que é uma linha?". No DW ele é escolhido para a
**análise**: a `fato_pedidos` tem uma linha por item, porque é assim que se
soma faturamento por produto. Num modelo, o grão é escolhido pela
**decisão**: o antifraude decide sobre **pedidos**, então a tabela de treino
tem uma linha por pedido.

Quando o grão está errado, três coisas acontecem ao mesmo tempo:

1. exemplos se repetem, e o modelo dá mais peso a quem tem mais linhas;
2. o mesmo exemplo cai no treino e no teste, e o teste mede memória;
3. as contagens ficam infladas sem nenhum erro aparecer.

**Hábito:** antes de escrever o SQL, calcule quantas linhas a tabela tem que
ter. Depois confira. Metade dos erros de grão aparece aqui.

**Técnica:** agregue **antes** de juntar. `GROUP BY id_pedido` na fato de
itens, e só então `JOIN` com as dimensões.

## 3. O passado na dimensão: SCD tipo 2

A `dim_pessoas` guarda uma versão por endereço. A fato aponta para a
**versão** (`sk_pessoa`), não para a pessoa (`id`). Duas consequências:

* juntar pelo `id` traz **todas** as versões e multiplica as linhas;
* a pergunta certa para um modelo é "onde a pessoa morava **no dia** da
  compra?", e a resposta está em `dt_inicio` e `dt_fim`.

Essa junção pela chave **e** pelo tempo é o ***as-of join***:

```sql
JOIN dim_pessoas v
  ON v.id = x.id_pessoa
 AND x.data >= v.dt_inicio
 AND x.data <  COALESCE(v.dt_fim, 'infinity')
```

## 4. Vazamento: o futuro dentro da tabela

**Vazamento** (*leakage*) é qualquer informação na tabela de treino que não
existiria no momento de usar o modelo. O modelo aprende a usá-la, fica ótimo
no notebook e falha em produção. A etapa 2 mostra três tipos:

| Tipo | Exemplo | Por que engana |
|---|---|---|
| **Vazamento de alvo** | `taxa_fraude_cliente` calculada com todos os pedidos do cliente | contém o próprio rótulo |
| **Vazamento temporal** | `status` = cancelado | só existe dias depois da compra |
| **Atributo calculado com o futuro** | `qtd_contas` da `dim_dispositivo` | é o total até a foto, não até a compra |

**Teste mental para cada coluna:** "no segundo em que o cliente clicou em
comprar, este valor já existia, **com este número**?"

**Técnica:** janelas que terminam **antes** do momento da decisão:

```sql
sum(pedidos_no_dia) OVER (PARTITION BY id_pessoa ORDER BY data
                          ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
```

O `1 PRECEDING` é a diferença entre "até ontem" e "até agora, inclusive o que
eu quero prever".

## 5. A feature table point-in-time

Calcular as features do cliente dentro de cada tabela de treino é repetir
trabalho e repetir erros. A solução da indústria é a ***feature table***: uma
tabela com o estado de cada entidade **em cada instante** (aqui, cada cliente
em cada dia). Qualquer modelo junta com ela pelo momento da decisão:

```sql
JOIN analytics.fs_cliente fs
  ON fs.id_pessoa = pedido.id_pessoa
 AND fs.data      = pedido.dt_venda::date
```

É o que as *feature stores* (Feast, Tecton, Databricks...) fazem por baixo:
guardar features com tempo e servir a versão certa para cada instante.

## 6. O rótulo também tem tempo

O rótulo não nasce junto com o evento:

* a **fraude** é confirmada por um analista, até 4 dias depois;
* a **entrega** só tem desfecho quando o caminhão chega;
* a **recompra** só se sabe quando o mês seguinte termina.

Dois conceitos saem daí:

| Conceito | O que é | O que fazer |
|---|---|---|
| **Maturação** | o tempo até o rótulo se tornar confiável | rótulo **nulo** enquanto não amadurece (`is_fraude` nos últimos 7 dias) |
| **Censura** | o desfecho ainda não aconteceu para parte dos casos, e os que já têm desfecho não são uma amostra justa | só julgar quem teve tempo (`atrasou` só para saídas com mais de 10 dias) |

**Nulo não é falso.** "Ainda não sabemos" e "não é fraude" são afirmações
diferentes, e o modelo precisa receber só a segunda.

## 7. A divisão temporal

`train_test_split` sorteia linhas. Em produção, o modelo sempre prevê o
**futuro** com o **passado**. A divisão honesta reproduz isso:

```text
|---------- treino ----------|------ teste ------|-- sem_rotulo --|
                         foto - 60 dias      foto - 7 dias        foto
```

A coluna `particao` faz parte da tabela: quem usar a tabela não precisa
decidir a divisão (nem errá-la).

## 8. A grade

`GROUP BY` só cria linhas para o que **aconteceu**. Mas, para um modelo, o
que não aconteceu também é dado:

| Tabela | O que some sem a grade |
|---|---|
| `fs_cliente` | os dias sem compra (e as janelas por linhas deixam de ser dias) |
| `ds_cliente_mes` | os meses sem compra: o cliente que sumiu, exatamente quem o CRM quer achar |
| `ds_peso_dia` | os dias sem caminhão: o `LAG(7)` deixa de ser "7 dias atrás" |

**Técnica:** primeiro a grade (entidade × calendário, com a `dim_tempo`),
depois `LEFT JOIN` dos eventos, com `COALESCE(..., 0)`.

## 9. Formato longo e largo

| Formato | Uma linha por | Bom para |
|---|---|---|
| **Longo** (*tidy*) | entidade **e** instante | guardar, filtrar, modelos que tratam várias séries juntas |
| **Largo** | instante, uma coluna por entidade | ver lado a lado, bibliotecas que esperam uma coluna por série |

O dado é o mesmo. `pivot` vai de longo para largo; `melt`, de largo para
longo. Guarde no longo, transforme na hora de ler.

## 10. Resumo: as perguntas antes de qualquer tabela de treino

1. **Qual o grão?** Quantas linhas a tabela tem que ter?
2. **Qual o momento da decisão** de cada linha?
3. Cada feature **existia** nesse momento, com esse valor?
4. O rótulo já está **maduro**? E quem ainda não teve tempo?
5. A divisão de treino e teste respeita o **tempo**?
6. Os casos **sem evento** estão na tabela?

Se a resposta a todas for sim, o número que você vê no notebook é o número
que a empresa vai ter.
