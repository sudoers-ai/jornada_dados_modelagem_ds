# 🔗 Integração com os outros repositórios (opcional)

> ⬅️ [README principal](../README.md)

> 🛑 **Nada aqui é necessário para concluir a disciplina.** Este repositório
> é autocontido, e a trilha termina nos [desafios](../desafios/desafios.md).
> Esta página é para quem **também** cursou as outras partes da Jornada e
> quer enxergar como elas se encaixam.

## O que os repositórios têm em comum

Todos usam o mesmo universo, a Liga Sudoers, gerado com a **mesma semente**.
A pessoa de `id = 1` é o Thomas Camargo em todos. Isso não cria dependência:
cada repositório carrega a sua própria cópia do gerador.

| Repositório | O que ensina | Como se liga a este |
|---|---|---|
| [`liga_sudoers`](https://github.com/sudoers-ai/liga_sudoers) | OLTP, DW e ETL tradicionais (Apache Hop, Metabase) | o ponto de partida de toda a Jornada |
| [`jornada_dados`](https://github.com/sudoers-ai/jornada_dados) | CDC, Kafka, Spark, Delta Lake, dbt, Airflow | onde as tabelas desta disciplina rodariam em produção |
| [`jornada_dados_nosql`](https://github.com/sudoers-ai/jornada_dados_nosql) | Cinco bancos não relacionais | o grafo de aparelhos compartilhados é uma feature de fraude |
| [`jornada_dados_modelagem`](https://github.com/sudoers-ai/jornada_dados_modelagem) | Modelagem transacional e dimensional | constrói, passo a passo, o DW que este repositório **recebe pronto** |

## Ideia 1 — De onde veio o DW

O DW que você recebe aqui é o resultado da disciplina de modelagem para
engenheiros (`jornada_dados_modelagem`), com uma coluna a mais:
`fato_pedidos.dt_fraude`, a data em que a fraude foi confirmada. Ela é o que
torna possível falar de maturação do rótulo.

Se você fez as duas disciplinas, compare
[`modelagem/dbml/dw_recebido.dbml`](../modelagem/dbml/dw_recebido.dbml) com o
`05_evolucao_dw` de lá. Pergunta para pensar: que outras colunas de **data**
o engenheiro poderia ter guardado para facilitar a vida do cientista de dados?
(Dica: toda coluna que muda de valor merece uma data de quando mudou.)

## Ideia 2 — As tabelas `analytics` como modelos dbt

O `jornada_dados` tem um projeto dbt sobre a camada *gold*. As cinco tabelas
desta disciplina são candidatas naturais a modelos dbt: cada gabarito em
[`modelagem/gabarito/`](../modelagem/gabarito/) é um `SELECT` que vira um
arquivo `.sql` de modelo, e o contrato `analytics.dbml` vira o `schema.yml`
com os testes `unique` (o grão) e `not_null`. É o desafio Sênior nº 4, levado
a sério.

## Ideia 3 — O anel de fraude como grafo

No `jornada_dados_nosql`, o Neo4j mostra os aparelhos compartilhados por
várias contas como um grafo. Aqui, a mesma ideia virou uma feature:
`qtd_outras_contas_no_dispositivo`. Uma extensão natural é calcular, no grafo,
o tamanho do componente conectado de cada aparelho **até a data da compra** e
trazê-lo como feature. O cuidado é o mesmo da etapa 4: o grafo de hoje não é
o grafo do dia da compra.
