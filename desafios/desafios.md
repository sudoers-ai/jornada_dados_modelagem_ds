# 🧪 Desafios da Jornada — Modelagem de Dados para Cientistas de Dados

> ⬅️ Anterior: [7. O rótulo definido por regra](../trilha/07_rotulo_por_regra/README.md) · [README principal](../README.md) · Etapa 8 de 8

A trilha guiada acabou. Aqui não há passo a passo: há o problema, o que conta
como evidência e o que entregar.

Escolha o seu nível. Cada desafio tem **tarefas**, **evidências** (o que
comprova que deu certo) e **entregáveis** (o que você vai postar ou commitar).

- [Nível Júnior](#-nível-júnior) — a trilha de ponta a ponta, explicada com as suas palavras
- [Nível Pleno](#-nível-pleno) — features e rótulos novos, sem roteiro
- [Nível Sênior](#-nível-sênior) — decisões de arquitetura, qualidade e operação

> **Dica:** conclua o Júnior antes, mesmo que você seja avançado. Ele garante
> que o ambiente está consistente, e os outros níveis partem dele.
>
> **Onde colocar o seu trabalho:** crie uma pasta `entregas/` na raiz do
> repositório. Notebooks novos podem ficar em `notebooks/` (crie com
> **File → New → Notebook** no JupyterLab e comece pela célula
> `from liga import sql, executar, conferir, avaliar, progresso`). Para rodar
> um SQL seu pelo terminal: `make sql f=entregas/arquivo.sql`.
>
> **Antes de mexer nas tabelas da trilha**, guarde o estado que passa nas
> provas. Se algo quebrar, `make gabarito t=<tabela>` devolve a versão certa.

---

## 🔹 Nível Júnior

**Foco:** percorrer a trilha inteira e provar que entendeu o porquê de cada
tabela.

### Tarefas

1. Concluir as etapas 1 a 7 **sem usar nenhum gabarito**.
2. Rodar as provas e guardar a saída: `make avaliar t=legado`,
   `make conferir`, `make avaliar t=fraude` e `make progresso`.
3. Escrever, em uma frase cada, o **grão** das cinco tabelas que você
   construiu, e quantas linhas cada uma tem e por quê (a conta, não só o
   número).
4. Explicar, com as suas palavras, cada um dos **sete erros** do notebook
   herdado: o que a coluna dizia, o que ela deveria dizer, e como a sua tabela
   resolve.
5. Fazer o **"experimente errar"** em duas tabelas diferentes (a da etapa 3 e
   mais uma, à sua escolha): quebrar uma regra de propósito, guardar a saída
   da conferência e explicar por que ela aponta aquela coluna.
6. Usando só a `analytics.fs_cliente`, responder: quantos clientes tinham pelo
   menos 3 pedidos no início do dia 1º de julho de 2026? E no início do dia 1º
   de agosto?

### Evidências mínimas

* `make progresso` com **6 de 6**.
* As duas saídas do `make avaliar` lado a lado, com uma frase explicando a
  diferença.
* As duas saídas do "experimente errar".

### Entregáveis

* Um documento `entregas/junior.md` com as respostas das tarefas 3 a 6.
* Um *post* (LinkedIn, blog) explicando, para quem não é da área, por que um
  modelo com AUC de 0,99 pode não funcionar.

---

## 🔸 Nível Pleno

**Foco:** criar features e rótulos novos sem roteiro, sem quebrar a promessa
sobre o tempo.

### Tarefas

1. **A taxa de fraude honesta.** O notebook herdado usava
   `taxa_fraude_cliente` com vazamento. Crie a versão honesta: a fração dos
   pedidos **anteriores** do cliente que já tinham sido **confirmados como
   fraude** (`dt_fraude`) **antes** do momento da compra. Acrescente-a como
   coluna a mais na `analytics.ds_pedido_fraude` (colunas a mais não quebram
   a conferência) e rode `make avaliar t=fraude`. O modelo melhorou? Por quê?
2. **Uma feature de velocidade.** "Quantos pedidos o cliente fez nas últimas
   24 horas antes desta compra" (horas, não dias: a `fs_cliente` não serve,
   porque está no grão do dia). Acrescente, avalie e explique.
3. **Prove que não há vazamento.** Para cada coluna nova, escreva uma consulta
   que mostre que ela só usa dados anteriores à compra (por exemplo: compare o
   valor calculado com a tabela inteira e com a tabela cortada na data da
   compra, para alguns pedidos).
4. **Um rótulo novo: devolução.** Construa `analytics.ds_pedido_devolucao`:
   um pedido por linha, rótulo `devolveu`. Defina você a maturação (quanto
   tempo depois da entrega uma devolução ainda acontece? Meça no DW) e a
   partição temporal. Documente o grão e a regra de cada coluna num arquivo
   `entregas/ds_pedido_devolucao.dbml`, no mesmo formato do
   `analytics.dbml`.
5. **Série com sazonalidade.** Na `ds_peso_dia`, a média de 7 dias anteriores
   ignora o dia da semana. Crie `media_mesmo_dia_4_semanas`: a média das 4
   últimas ocorrências do **mesmo dia da semana**. Mostre num gráfico se ela
   acompanha a série melhor que a média de 7 dias.

> ⚠️ O `avaliar` sabe o valor "de produção" apenas das colunas do contrato.
> As colunas novas que você acrescentar entram no modelo **com o valor que
> você calculou**: se houver vazamento nelas, ele aparece nos dois números,
> notebook e produção. Por isso a tarefa 3 existe.

### Evidências mínimas

* `make conferir t=ds_pedido_fraude` continua ✅ (com o aviso de colunas a
  mais) depois das tarefas 1 e 2.
* A saída do `make avaliar t=fraude` antes e depois.
* A consulta da tarefa 3 e o resultado dela.
* O `.dbml` e o SQL da tarefa 4.

### Entregáveis

* `entregas/pleno.md` com a explicação de cada feature e o efeito dela.
* `entregas/*.sql` com o SQL de cada tabela e coluna nova.
* `entregas/ds_pedido_devolucao.dbml`.

---

## 🟣 Nível Sênior

**Foco:** decisões que valem para um time inteiro, e não para uma tabela.

### Tarefas

1. **Escolha a janela de maturação com dados.** A trilha usa 7 dias para a
   fraude e 10 para a entrega. Mostre, com consultas no DW, a distribuição
   do tempo até o rótulo (confirmação da fraude, chegada do caminhão) e
   defenda o número que você usaria. Qual o custo de um número maior? E de
   um menor?
2. **A feature store incremental.** A `fs_cliente` é reconstruída inteira a
   cada execução. Escreva a versão incremental: só calcula os dias novos,
   sem recalcular o passado, e dá o mesmo resultado que a versão completa.
   Prove a igualdade com uma consulta (`EXCEPT` nos dois sentidos).
3. **Testes de dados.** Escreva, em SQL, os testes que um time rodaria todo
   dia nas cinco tabelas: grão sem repetição, contagem esperada (a grade),
   nulos onde a regra manda, e **nenhuma feature com data maior que o
   momento da decisão**. Organize como uma lista que retorna zero linhas
   quando está tudo certo.
4. **Do SQL ao dbt.** Esboce como estas cinco tabelas virariam modelos dbt:
   quais seriam `ref()`, quais seriam incrementais, que testes ficariam no
   `schema.yml`. Não precisa rodar; precisa decidir e justificar.
5. **Monitoramento.** Uma semana depois de colocar o modelo em produção,
   como você saberia que ele piorou, se o rótulo só chega dias depois?
   Proponha as métricas (sem rótulo e com rótulo) e a tabela que as
   guardaria, com o grão dela.

### Evidências mínimas

* As consultas e os gráficos da tarefa 1.
* A prova de igualdade da tarefa 2.
* Os testes da tarefa 3 rodando e retornando zero linhas.

### Entregáveis

* `entregas/senior.md` com as decisões, as justificativas e os
  *trade-offs*.
* `entregas/*.sql` com o código.

---

## Como saber se ficou bom

* Toda tabela nova tem o **grão** escrito e a contagem esperada conferida.
* Toda coluna nova responde "sim" a: "existia no momento da decisão, com
  este valor?".
* Todo rótulo novo tem a **maturação** decidida, e os casos imaturos ficam
  **nulos**.
* Toda divisão de treino e teste é **temporal**.

---

# 🏁 Fim da trilha

Você chegou ao fim da disciplina. Volte ao [README principal](../README.md)
e, se quiser, veja como este repositório se conecta aos outros da Jornada em
[integracao/](../integracao/README.md).
