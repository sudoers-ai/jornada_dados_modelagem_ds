# 📖 Glossário

> ⬅️ [README principal](../README.md)

Os termos da disciplina, cada um com um exemplo da Liga Sudoers. Para a
explicação completa, veja [Do star schema à tabela de treino](./modelagem.md).

| Termo | Em uma frase | Na Liga Sudoers |
|---|---|---|
| **Data Warehouse (DW)** | Banco desenhado para **ler** muito dado de uma vez e responder perguntas | O banco `liga_sudoers_dw` |
| **Star schema** | Fatos (o que aconteceu, com números) no centro, dimensões (o contexto) em volta | `fato_pedidos` ligada a `dim_pessoas`, `dim_produtos`... |
| **Grão** | O que é **uma linha** de uma tabela | `fato_pedidos`: um item; `ds_pedido_fraude`: um pedido |
| **SCD tipo 2** | Dimensão que guarda o passado: uma versão nova a cada mudança, com validade | O Ravi Rios tem duas linhas na `dim_pessoas`, uma por cidade |
| **Chave substituta (`sk_`)** | A chave do DW, que aponta para **uma versão** | `sk_pessoa` 7 é o Ravi em Barbosa das Pedras; 8, em Souza |
| **Feature** | Uma coluna que o modelo usa para prever | `qtd_pedidos_30d` |
| **Rótulo (alvo, *target*)** | A coluna que o modelo tenta prever | `is_fraude`, `atrasou`, `comprou_mes_seguinte` |
| **Feature table** | Tabela de features de uma entidade ao longo do tempo | `fs_cliente`: cada cliente em cada dia |
| ***Point-in-time*** | O valor que uma coluna tinha **num instante** do passado | a UF do cliente **no dia da compra** |
| ***As-of join*** | Junção pela chave **e** pelo tempo: "a versão que valia naquele momento" | `data >= dt_inicio AND data < dt_fim` |
| **Vazamento (*leakage*)** | Informação na tabela de treino que não existiria na hora de prever | `status` cancelado; `qtd_contas` final |
| **Vazamento de alvo** | Uma feature calculada com o próprio rótulo | `taxa_fraude_cliente` do notebook herdado |
| **Maturação do rótulo** | O tempo até o rótulo se tornar confiável | a fraude leva até 4 dias para ser confirmada |
| **Rótulo nulo** | "Ainda não sabemos", diferente de "não" | `is_fraude` nulo nos últimos 7 dias |
| **Divisão temporal** | Treinar no passado e testar no futuro, nunca sortear | `particao`: `treino`, `teste`, `sem_rotulo` |
| **Grade** | Todas as combinações de entidade × tempo, com ou sem evento | 500 clientes × 181 dias na `fs_cliente` |
| **Painel (*panel data*)** | Muitas entidades observadas ao longo de vários períodos | `ds_cliente_mes` |
| **Série temporal** | Uma medida ao longo do tempo, um ponto por intervalo | `ds_peso_dia` |
| **Janela (*window*)** | Cálculo sobre linhas vizinhas, sem agrupar | `sum(...) OVER (... ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING)` |
| **`LAG` / `LEAD`** | O valor da linha anterior / seguinte | `LAG(peso, 7)`: 7 **linhas** atrás (7 dias só com a grade) |
| **Censura** | Casos cujo desfecho ainda não aconteceu | caminhões que ainda estão na estrada |
| **Formato longo × largo** | Uma linha por medida × uma coluna por série | `ds_peso_dia` (longo) × `pivot` por transportadora (largo) |
| **AUC** | Nota de 0,5 (sorteio) a 1 (perfeito) da capacidade de ordenar fraudes antes das não fraudes | 0,986 no notebook herdado, 0,627 em produção |
| **PR-AUC** | Parecida com a AUC, mais exigente quando o rótulo é raro | 0,736 na tabela de treino correta |
