# 🧪 Liga Sudoers — Modelagem de Dados para Cientistas de Dados

![Desafio Engenheiro de Dados](Desafio%20-%20Jornada%20Engenharia%20de%20Dados.png "Desafio Engenheiro de Dados")

> Parte da **Jornada de Dados**. Na disciplina de modelagem para engenheiros
> ([`jornada_dados_modelagem`](https://github.com/sudoers-ai/jornada_dados_modelagem)),
> o transacional vira um Data Warehouse. Aqui o Data Warehouse vira **tabelas que um
> modelo de machine learning consegue usar sem ser enganado**.
>
> Este repositório é **autocontido**: não depende de nenhum outro. Você só precisa de
> Docker e `make`.

Bem-vindo ao Mapa do Cientista de Dados, módulo **Modelagem de Dados**. Você entra na
Liga Sudoers como cientista de dados e herda duas coisas: um Data Warehouse bem feito e
um notebook de antifraude que dizia ter **AUC de 0,99** — e que, em produção, não pegava
nem metade das fraudes.

O algoritmo estava certo. A **tabela** estava errada. Esta disciplina é sobre isso.

---

## 🎯 O que você vai aprender

Não é "como treinar um modelo" (o modelo aqui é sempre o mesmo, simples e fixo). É **como
desenhar a tabela que o modelo recebe**, porque é nela que mora a maior parte dos erros
que fazem um modelo funcionar no notebook e falhar em produção.

| Conceito | A pergunta que ele responde |
|---|---|
| **Grão** | "O que é uma linha da minha tabela de treino?" |
| ***Point-in-time*** | "O que se sabia **naquele momento**?" |
| **Vazamento de dados** | "Esta coluna existe na hora em que o modelo vai ser usado?" |
| **Maturação do rótulo** | "Este rótulo já pode ser confiado?" |
| **Divisão temporal** | "Estou testando o futuro ou o passado?" |
| **Grade completa** | "E os dias, meses e clientes **sem** evento?" |
| **Censura** | "Quem ainda não teve tempo de acontecer pode ser julgado?" |

Ao final você terá construído **cinco tabelas** da camada analítica, cada uma conferida
linha a linha contra o modelo de referência, e visto com os próprios olhos a diferença
entre um número de notebook e um número de produção.

---

## 🧭 Como a disciplina funciona

```
  VOCÊ CONSTRÓI              O REPOSITÓRIO CONFERE               VOCÊ VÊ O EFEITO
┌─────────────────┐       ┌───────────────────────────┐       ┌──────────────────────┐
│ notebook guiado │       │ make conferir t=<tabela>  │       │ make avaliar         │
│ no JupyterLab   │ ────► │                           │ ────► │                      │
│ (SQL + pandas)  │       │ ✅ igual à referência     │       │ notebook × produção  │
│                 │       │ ❌ diz a coluna e a linha │       │                      │
└─────────────────┘       └───────────────────────────┘       └──────────────────────┘
```

1. **Cada etapa é um notebook guiado.** Ele explica o motivo, mostra o erro comum
   acontecendo e depois constrói a tabela certa. Você roda célula por célula.
2. **O modelo já está desenhado.** O contrato das cinco tabelas está em
   [`modelagem/dbml/analytics.dbml`](./modelagem/dbml/analytics.dbml): o grão, as
   colunas e a regra de cada uma.
3. **Toda etapa termina com uma prova.** A conferência compara a sua tabela com a
   referência — estrutura, grão e conteúdo, linha a linha. Se uma feature sua usar
   informação do futuro, ela aponta a coluna, mostra um exemplo e dá uma dica.
4. **Um placar mostra o seu avanço.** `make progresso` (ou `progresso()` no notebook).
5. **Travou?** Toda tabela tem gabarito: `make gabarito t=<tabela>`.

---

## ✅ Pré-requisitos

* [ ] **Docker** e **Docker Compose v2**
* [ ] **`make`** — todos os comandos da trilha começam com ele
* [ ] ~2 GB de RAM livres e ~2 GB de disco
* [ ] Um navegador (o JupyterLab abre nele)

> **Você não precisa instalar Python, Jupyter, pandas nem PostgreSQL.** Tudo roda
> dentro de containers.

### 🪟 Estou no Windows (a maioria da turma)

Siga primeiro o guia **[Preparando o Windows](./docs/windows.md)**. Ele instala o WSL2,
o Docker Desktop e o `make`, e baixa o repositório no lugar certo. Leva uns 20
minutos, uma vez só.

> ⚠️ No Windows, **todos os comandos da trilha são digitados no terminal do Ubuntu
> (WSL)**, nunca no PowerShell. O JupyterLab, esse sim, você abre no navegador do
> próprio Windows.

Ao terminar o guia, continue do passo [3. Confira o terreno](#3-confira-o-terreno).

### 🐧 Estou no Linux ou no Mac

Além do Docker, falta só o `make`, que não vem com o Docker:

| Sistema | Como instalar |
|---|---|
| Ubuntu / Debian | `sudo apt update && sudo apt install make` |
| Fedora | `sudo dnf install make` |
| Mac | `xcode-select --install` |

---

## ▶️ Começando em 5 minutos

### 1. Baixe o repositório

```bash
cd ~
git clone https://github.com/sudoers-ai/jornada_dados_modelagem_ds.git
cd jornada_dados_modelagem_ds
```

(No Windows você já fez isso no [guia de preparação](./docs/windows.md).)

### 2. Confira se você tem o `make`

<!-- rodar: shell -->
```bash
make --version
```

```text
GNU Make 4.3
```

Se aparecer `make: command not found`: no Windows, você provavelmente está no
PowerShell — abra o terminal do **Ubuntu**. No Linux ou no Mac, instale com a tabela
acima.

### 3. Confira o terreno

<!-- rodar: shell -->
```bash
make verificar
```

```
Conferindo o ambiente

  ✅ Docker respondendo (29.9.0)
  ✅ Docker Compose v2 (5.6.0)
  ✅ porta 5450 livre (PostgreSQL (o Data Warehouse))
  ✅ porta 8899 livre (JupyterLab)
  ✅ memória disponível para o Docker: 31 GB

Tudo certo. Próximo passo: make subir
```

### 4. Suba o ambiente

<!-- rodar: shell -->
```bash
make subir
```

Na primeira vez ele baixa e monta as imagens (alguns minutos) e **carrega o Data
Warehouse** (menos de um minuto). No fim:

```
...
 itens_vendidos | pedidos | clientes |     de     |    ate
----------------+---------+----------+------------+------------
          14976 |    5000 |      500 | 2026-03-05 | 2026-09-01
(1 row)

✅ Data Warehouse carregado.

  Tudo no ar. Abra o JupyterLab: http://localhost:8899
  e continue em trilha/01_conhecer_o_dw/README.md
```

Nas próximas vezes, `make subir` é rápido e **não apaga o seu trabalho**: ele avisa que
o DW já está carregado.

### 5. Abra o JupyterLab

No navegador (no Windows, o navegador do próprio Windows): **http://localhost:8899**

Abre direto na pasta `notebooks`, com os sete notebooks da trilha. Não pede senha.

### 6. Confira o seu placar

<!-- rodar: shell -->
```bash
make progresso
```

```
O seu placar

  Etapa 1  Conhecer o DW                      (leitura)
  Etapa 2  O notebook herdado                 ⏳ falta rodar o notebook
  Etapa 3  Feature table do cliente           ⏳ a fazer
  Etapa 4  Tabela de treino do antifraude     ⏳ a fazer
  Etapa 5  Painel cliente × mês               ⏳ a fazer
  Etapa 6  Série temporal do peso             ⏳ a fazer
  Etapa 7  Rótulo por regra: entregas         ⏳ a fazer

  ░░░░░░  0 de 6 etapas com prova concluídas
```

Ao longo da trilha ele vai ficando verde.

---

## 🗺️ A trilha

Cada etapa tem um **roteiro** (README da pasta `trilha/`) e um **notebook** (pasta
`notebooks/`). Leia o roteiro, depois abra o notebook. Siga na ordem.

| # | Etapa | Notebook | Você constrói | A prova |
|---|---|---|---|---|
| 1 | [Conhecer o DW](./trilha/01_conhecer_o_dw/README.md) | `01_conhecer_o_dw` | — | entender o grão de cada fato |
| 2 | [O notebook herdado](./trilha/02_notebook_herdado/README.md) | `02_notebook_herdado` | — | `make avaliar t=legado` |
| 3 | [Feature table do cliente](./trilha/03_feature_table/README.md) | `03_feature_table` | `fs_cliente` | `make conferir t=fs_cliente` |
| 4 | [Tabela de treino](./trilha/04_tabela_de_treino/README.md) | `04_tabela_de_treino` | `ds_pedido_fraude` | `make conferir` e `make avaliar t=fraude` |
| 5 | [Painel cliente × mês](./trilha/05_painel/README.md) | `05_painel` | `ds_cliente_mes` | `make conferir t=ds_cliente_mes` |
| 6 | [Série temporal](./trilha/06_serie_temporal/README.md) | `06_serie_temporal` | `ds_peso_dia` | `make conferir t=ds_peso_dia` |
| 7 | [Rótulo por regra](./trilha/07_rotulo_por_regra/README.md) | `07_rotulo_por_regra` | `ds_entrega` | `make conferir t=ds_entrega` |
| 8 | [Desafios](./desafios/desafios.md) | — | o que você quiser | os seus entregáveis |

Tempo estimado: de 4 a 6 horas. O ambiente guarda o seu progresso entre uma aula e
outra.

---

## 🚪 O que subiu

| Serviço | Endereço | Para quê |
|---|---|---|
| **JupyterLab** | http://localhost:8899 | onde você trabalha |
| **PostgreSQL** | `localhost:5450`, banco `liga_sudoers_dw`, usuário `sudoers`, senha `password` | o Data Warehouse (se quiser usar DBeaver ou outro cliente) |

O banco tem três *schemas* que importam:

| Schema | O que tem | Quem escreve |
|---|---|---|
| `public` | o Data Warehouse que você recebeu: 7 dimensões e 4 fatos | ninguém (é a fonte) |
| `analytics` | as **suas** tabelas | você |
| `legado` | o dataset do notebook herdado | o notebook da etapa 2 |

---

## 📚 Material de apoio

* [📐 Do star schema à tabela de treino](./docs/modelagem.md) — o texto que explica o **porquê** de tudo
* [📖 Glossário](./docs/glossario.md) — grão, point-in-time, vazamento, censura... em português claro
* [🪟 Preparando o Windows](./docs/windows.md) — WSL2, Docker Desktop e `make`
* [✅ Checklist do aluno](./docs/checklist.md) — para marcar o que já fez
* [🔎 Validação por evidências](./docs/validacao_evidencia.md) — o comando de prova de cada etapa
* [❓ FAQ](./docs/faq.md) — erros comuns e como resolver
* [⌨️ Comandos](./docs/comandos.md) — todo `make` e o que ele faz
* [👩‍💻 Perfis](./docs/perfis.md) — cientista de dados, engenheiro de ML, analytics engineer
* [📐 Os modelos e o contrato](./modelagem/README.md) — os `.dbml`, os diagramas e o gabarito
* [🏗️ De onde vem o DW](./carga/README.md) — o gerador, o transacional e o ETL
* [🔗 Integração com os outros repositórios](./integracao/README.md) — **opcional**

---

## 🧰 Comandos do dia a dia

```bash
make ajuda          # lista todos os comandos
make progresso      # o seu placar
make conferir       # confere todas as suas tabelas
make derruba        # para tudo, MANTENDO o seu trabalho (use ao fim da aula)
make subir          # volta de onde parou
make diagnostico    # relatório completo para mandar ao instrutor
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.

## 📜 Licença

Este projeto está licenciado sob a **Licença SUDOERS**.

---

# ➡️ Comece em [trilha/01_conhecer_o_dw/README.md](./trilha/01_conhecer_o_dw/README.md)
