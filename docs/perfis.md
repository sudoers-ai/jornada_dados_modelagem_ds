# 👩‍💻 Perfis e responsabilidades

> ⬅️ [README principal](../README.md)

Nesta disciplina você faz, sozinho, o trabalho de três profissionais. Num time
de verdade eles são pessoas diferentes, e as tabelas da camada `analytics`
ficam exatamente na fronteira entre eles. Saber quem é dono de quê é parte de
ser sênior.

> **Dica:** ao fim de cada etapa, pergunte-se: "quem do time teria feito
> isto? E quem teria que ser avisado?"

---

## Cientista de Dados

Faz a pergunta de negócio virar um problema de previsão, e avalia se a
resposta presta.

**Responsabilidades:**

* Definir **o que prever** e **em que momento** a previsão é feita.
* Definir o rótulo, inclusive quando ele não existe pronto (etapa 7).
* Escolher a métrica e a forma honesta de medi-la.
* Desconfiar de números bons demais.

**Onde aparece na trilha:**

| Etapa | O que o cientista de dados faz |
|---|---|
| 2 | Desconfia do AUC de 0,99 e investiga |
| 4 | Define rótulo maduro e divisão temporal |
| 7 | Define "atrasou" e trata a censura |

**A pergunta que ele sempre faz:** "isto existia no momento da decisão?"

---

## Engenheiro de Machine Learning

Leva o modelo para produção e garante que ele recebe, em produção, **os mesmos
dados** que recebeu no treino.

**Responsabilidades:**

* Manter a *feature store* (a `fs_cliente` é uma).
* Garantir que a feature calculada no treino é a mesma servida em produção.
* Monitorar o modelo: queda de desempenho, mudança nos dados.

**Onde aparece na trilha:**

| Etapa | O que o engenheiro de ML faz |
|---|---|
| 2 | Percebe que `status` e `qtd_contas` não existem na hora da compra |
| 3 | Constrói uma *feature table* reutilizável, sem futuro |
| 4 | Compara "no notebook" com "em produção" (o `avaliar`) |

**A pergunta que ele sempre faz:** "essa coluna vai estar disponível, com esse
valor, quando o modelo for chamado?"

---

## Analytics Engineer

Transforma o DW em tabelas **prontas para consumo**, testadas e documentadas.
Aqui, o consumidor é um modelo.

**Responsabilidades:**

* Modelar a camada analítica (hoje, quase sempre com dbt).
* Escrever o **contrato** de cada tabela: grão, colunas, regra de cada uma.
* Testar: grão sem repetição, contagens, conteúdo.

**Onde aparece na trilha:**

| Etapa | O que o analytics engineer faz |
|---|---|
| 3 a 7 | Escreve o SQL de cada tabela seguindo o contrato (`analytics.dbml`) |
| 5 e 6 | Monta a grade com a `dim_tempo` |
| todas | Confere estrutura, grão e conteúdo (o `conferir` é um teste de dados) |

**A pergunta que ele sempre faz:** "o que é uma linha desta tabela, e quantas
ela tem que ter?"

---

## Quem avisa quem

| Quando... | Quem avisa | Quem precisa saber |
|---|---|---|
| a engenharia muda o ETL do DW (uma coluna nova, uma regra nova) | engenheiro de dados | analytics engineer: as tabelas `analytics` podem mudar |
| uma feature nova entra no modelo | cientista de dados | engenheiro de ML: ela precisa existir em produção |
| a regra do rótulo muda (ex.: prazo de confirmação da fraude) | negócio | cientista de dados: a maturação muda |
| o modelo cai em produção | engenheiro de ML | cientista de dados e analytics engineer |
