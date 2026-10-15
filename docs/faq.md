# ❓ FAQ de aula — erros comuns e soluções

> ⬅️ [README principal](../README.md)

Antes de qualquer coisa, dois comandos resolvem ou explicam a maioria dos
problemas:

```bash
make status         # os 2 containers estão healthy?
make diagnostico    # relatório completo para mandar ao instrutor
```

---

## Subindo o ambiente

### `make verificar` diz que uma porta está ocupada

Outro programa usa a porta 5450 (banco) ou a 8899 (JupyterLab). Abra o
arquivo `.env` na raiz do repositório e troque a porta pela sugerida na
mensagem, por exemplo:

```text
PORTA_JUPYTER=8999
```

Salve e rode `make subir`. O JupyterLab passa a abrir em
http://localhost:8999 (o `make jupyter` mostra o endereço certo).

### `make subir` falha com `ports are not available` ou `address already in use`

É o mesmo caso de cima, com uma diferença: no Windows, um programa do próprio
Windows (um Jupyter do Anaconda, por exemplo) pode ocupar a porta sem que o
`make verificar`, que roda dentro do WSL, consiga ver. A solução é a mesma:
troque a porta no `.env` e rode `make subir` de novo.

### `docker: 'compose' is not a docker command`

Falta o Docker Compose v2. No Linux: `sudo apt install docker-compose-plugin`.
No Windows e no Mac ele já vem com o Docker Desktop: atualize o Docker Desktop.

### `permission denied while trying to connect to the Docker daemon`

No Linux, o seu usuário não está no grupo `docker`:

```bash
sudo usermod -aG docker $USER
```

Saia da sessão e entre de novo (ou reinicie). No Windows, abra o Docker Desktop.

### Estou no Windows e nada funciona

Confira as três regras do [guia do Windows](./windows.md): comandos no
terminal do **Ubuntu** (não no PowerShell), Docker Desktop **aberto**, e
repositório clonado dentro de `~` (não em `/mnt/c`).

### `make: command not found`

Você está no PowerShell (abra o Ubuntu) ou não instalou o `make`:

| Sistema | Como instalar |
|---|---|
| Windows (no Ubuntu do WSL) | `sudo apt update && sudo apt install make` |
| Ubuntu / Debian | `sudo apt update && sudo apt install make` |
| Mac | `xcode-select --install` |

### A primeira vez do `make subir` está demorando

Normal: ele baixa as imagens do PostgreSQL e do Python e instala as
bibliotecas (pandas, scikit-learn, JupyterLab). Leva de 3 a 10 minutos,
dependendo da internet. Nas próximas vezes leva segundos.

### `http://localhost:8899` não abre

1. `make status`: os dois containers estão `(healthy)`? Se o Jupyter estiver
   `(health: starting)`, espere meio minuto.
2. Se algum estiver parado: `make subir`.
3. Trocou a porta no `.env`? Use o endereço que o `make jupyter` mostra.

### O JupyterLab pede *token* ou senha

Você abriu **outro** Jupyter (o do Anaconda, por exemplo). O da disciplina não
pede senha e abre direto na pasta `notebooks`. Confira a porta no endereço.

### Subi, derrubei e os dados sumiram

`make derruba` **não** apaga nada. Quem apaga é `make limpar` (apaga o banco)
e `make carregar args=--limpar` (apaga o banco e carrega de novo). Os
notebooks nunca são apagados: eles moram na pasta `notebooks/` do repositório.

### Quero recomeçar do zero

```bash
make limpar
make subir
```

As suas tabelas somem; os notebooks continuam como você os salvou. Para
voltar um notebook ao original:

```bash
git checkout notebooks/03_feature_table.ipynb
```

---

## Nos notebooks

### `ModuleNotFoundError: No module named 'liga'`

O notebook foi aberto fora do JupyterLab da disciplina (no VS Code do
Windows, num Jupyter do Anaconda...). Use http://localhost:8899.

### `NameError: name '...' is not defined`

Você pulou uma célula, ou o *kernel* reiniciou e perdeu as variáveis. Rode o
notebook de novo desde o início: menu **Run → Run All Cells**.

### `❌ O banco recusou o comando: ...`

O SQL da célula tem um erro, e o banco diz qual. Se você editou a célula e não
sabe o que mudou, desfaça com `Ctrl + Z` ou restaure a tabela com
`make gabarito t=<tabela>`. Para voltar o notebook inteiro ao original:
`git checkout notebooks/<arquivo>.ipynb`.

### `could not connect to server` ou `Connection refused`

O banco caiu ou está subindo. `make status`; se precisar, `make consertar`.
Depois, no JupyterLab, **Kernel → Restart Kernel** e rode o notebook de novo.

### `relation "fato_pedidos" does not exist`

O DW não foi carregado (ou foi apagado com `make limpar`). Rode `make subir`
ou `make carregar`.

### `relation "analytics.fs_cliente" does not exist`

A etapa 4 depende da tabela da etapa 3. Faça a etapa 3, ou aplique a resposta
dela: `make gabarito t=fs_cliente`.

### A célula fica com `[*]` e não termina

Algumas células treinam modelos ou constroem tabelas de 90 mil linhas: levam
alguns segundos. Se passar de 2 minutos, **Kernel → Interrupt Kernel** e rode
de novo. Se continuar, `make diagnostico`.

### `Permission denied` ao salvar o notebook

O repositório foi clonado com `sudo`, ou os arquivos têm outro dono. Na pasta
do repositório:

```bash
sudo chown -R $USER:$USER .
make consertar
```

### Salvei o notebook e não sei onde ele foi parar

Na pasta `notebooks/` do repositório. No Windows, `explorer.exe notebooks`
(no terminal do Ubuntu) abre a pasta no Explorador de Arquivos.

---

## Nas provas

### A conferência diz `❌ ... linhas diferentes da referência`

A sua tabela tem a estrutura certa, mas uma coluna tem valores diferentes do
contrato. A conferência mostra **um exemplo** (a linha, o seu valor e o
esperado) e **uma dica**. Volte ao contrato
([`modelagem/dbml/analytics.dbml`](../modelagem/dbml/analytics.dbml)) e
compare a regra da coluna com o seu SQL.

### A conferência diz `linhas: X (esperado Y)`

Erro de **grão**. Mais linhas que o esperado: um `JOIN` multiplicou linhas.
Menos: faltou a **grade** (os dias ou meses sem evento).

### A conferência diz que falta uma coluna ou que o tipo está errado

O nome e o tipo têm que ser os do contrato. `integer` e `bigint` contam como
inteiro; `numeric` aceita qualquer número decimal.

### `make avaliar t=legado` termina com ❌

É o resultado **esperado** na etapa 2: é a prova de que o notebook herdado
mente. O ❌ que importa é o do `make avaliar t=fraude`, na etapa 4.

### `legado.dataset_fraude não existe`

Rode a Parte A do notebook `02_notebook_herdado` até a célula que salva o
dataset.

### Os meus números não batem com os do roteiro

Os dados são gerados com **semente fixa** e a foto do DW é sempre a mesma
(1º de setembro de 2026): todo aluno vê exatamente os mesmos números. Se não
bater, a tabela está diferente: rode `make conferir t=<tabela>`.

### Apliquei o gabarito e a conferência continua falhando

Rode `make carregar args=--limpar` (apaga tudo e carrega o DW de novo) e
`make gabarito t=<tabela>` para cada etapa na ordem. Se persistir, mande o
`make diagnostico` ao instrutor.

---

## Geral

### Posso usar DBeaver, pgAdmin ou outro cliente?

Pode. Conecte em `localhost`, porta `5450`, banco `liga_sudoers_dw`, usuário
`sudoers`, senha `password`. As suas tabelas ficam no schema `analytics`.

### Posso usar o VS Code em vez do JupyterLab?

Pode, para **ler** os arquivos (`code .` no terminal do Ubuntu). Para rodar os
notebooks, use o JupyterLab do navegador: é ele que tem o Python, as
bibliotecas e a conexão com o banco prontos.

### Este repositório precisa dos outros da Jornada?

Não. Ele é autocontido: traz o gerador de dados, o transacional, o ETL e o DW
prontos. As conexões com os outros repositórios estão em
[integracao/](../integracao/README.md) e são **opcionais**.

### Onde vejo os modelos como diagrama?

As imagens estão em `modelagem/img/`. Para navegar com zoom, cole o conteúdo
de um `.dbml` de `modelagem/dbml/` em [dbdiagram.io/d](https://dbdiagram.io/d).

### Como peço ajuda?

```bash
make diagnostico
```

Copie a saída inteira e mande ao instrutor, junto com o que você estava
fazendo e o erro que apareceu.
