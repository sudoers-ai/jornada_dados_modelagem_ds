# 🪟 Preparando o Windows

> ⬅️ [README principal](../README.md)

Este repositório roda em Linux. No Windows, isso se resolve com o **WSL2**: um
Linux de verdade rodando dentro do Windows, mantido pela Microsoft. Você
prepara uma vez e usa na disciplina inteira.

São quatro passos, cerca de 20 minutos (a maior parte é download).

| Passo | O que instala | Onde |
|---|---|---|
| 1 | WSL2 com Ubuntu | PowerShell |
| 2 | Docker Desktop, ligado ao WSL | Windows |
| 3 | `make` e `git` | terminal do Ubuntu |
| 4 | O repositório | terminal do Ubuntu |

> ⚠️ **A regra que evita quase todos os problemas:** depois do passo 1,
> **todos os comandos da trilha são digitados no terminal do Ubuntu**, nunca
> no PowerShell nem no Prompt de Comando. O PowerShell não tem `make` e não
> roda os scripts do repositório.

---

## Passo 1 — Instalar o WSL2 com Ubuntu

Abra o **PowerShell como administrador** (clique com o botão direito no menu
Iniciar → *Terminal (Admin)* ou *Windows PowerShell (Admin)*) e rode:

```powershell
wsl --install
```

**Reinicie o computador** quando terminar.

Depois de reiniciar, o Ubuntu abre sozinho e pede para você criar um **usuário
e uma senha do Linux**. Pode ser qualquer um; anote a senha, você vai usá-la
quando um comando começar com `sudo`. (Ao digitar a senha nada aparece na
tela. É normal.)

Confira, ainda no PowerShell:

```powershell
wsl -l -v
```

Tem que aparecer o Ubuntu com **VERSION 2**:

```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

> Se aparecer `VERSION 1`, converta com `wsl --set-version Ubuntu 2`.
>
> Se o `wsl --install` disser que o WSL já está instalado mas não houver
> nenhuma distribuição, rode `wsl --install -d Ubuntu`.

**Como abrir o terminal do Ubuntu daqui em diante:** menu Iniciar → digite
**Ubuntu** → Enter. É nele que você vai trabalhar.

---

## Passo 2 — Instalar o Docker Desktop

1. Baixe e instale o **Docker Desktop para Windows**:
   https://www.docker.com/products/docker-desktop
2. Abra o Docker Desktop e espere o ícone da baleia parar de se mexer.
3. Vá em **Settings** (a engrenagem) → **General** e confirme que
   **Use the WSL 2 based engine** está marcado.
4. Vá em **Settings → Resources → WSL Integration** e ligue a chave do
   **Ubuntu**. Clique em **Apply & restart**.

Confira, agora **no terminal do Ubuntu**:

```bash
docker --version
docker compose version
```

Os dois têm que responder com um número de versão.

> **O Docker Desktop precisa estar aberto** sempre que você for trabalhar na
> disciplina. Se o terminal responder
> `Cannot connect to the Docker daemon`, é porque ele está fechado.

---

## Passo 3 — Instalar o `make` e o `git`

No terminal do Ubuntu:

```bash
sudo apt update && sudo apt install -y make git
```

Confira:

```bash
make --version
```

```text
GNU Make 4.3
```

---

## Passo 4 — Baixar o repositório no lugar certo

No terminal do Ubuntu:

```bash
cd ~
git clone https://github.com/sudoers-ai/jornada_dados_modelagem_ds.git
cd jornada_dados_modelagem_ds
```

> ⚠️ **Clone dentro do Linux (`~`), e não numa pasta do Windows
> (`/mnt/c/...`).** O `cd ~` da primeira linha existe para isso. O Docker
> fica muito mais lento quando lê arquivos que estão no disco do Windows, e
> os finais de linha podem quebrar os scripts.

Pronto. Volte ao README principal e siga do passo
**[3. Confira o terreno](../README.md#3-confira-o-terreno)** (`make verificar`).

---

## Dicas para o dia a dia no Windows

**Abrir o JupyterLab.** Use o navegador do próprio Windows (Chrome, Edge,
Firefox): **http://localhost:8899**. Os containers rodam dentro do WSL, e o
Docker Desktop publica as portas no Windows. Você **não** precisa instalar
Python, Anaconda nem Jupyter no Windows.

> Já tem Jupyter ou Anaconda instalado no Windows? Sem problema: o da
> disciplina usa a porta **8899**, e não a 8888 de costume, justamente para
> os dois não brigarem. Só não confunda as abas: o da disciplina abre direto
> na pasta `notebooks`, com os sete notebooks da trilha.

**Onde ficam os notebooks que você salva.** Dentro do Linux, em
`~/jornada_dados_modelagem_ds/notebooks`. O `Ctrl + S` do JupyterLab grava
direto lá, e o seu trabalho continua lá depois de `make derruba`.

**Colar no terminal.** No terminal do Ubuntu, cole com `Ctrl+Shift+V` ou com
o **botão direito do mouse** (`Ctrl+V` nem sempre funciona).

**Ver os arquivos do repositório no Windows.** No terminal do Ubuntu, dentro
da pasta do repositório:

```bash
explorer.exe .
```

Abre o Explorador de Arquivos naquela pasta. Com o VS Code instalado,
`code .` abre o projeto inteiro.

**Um segundo terminal.** Se quiser rodar comandos `make` enquanto usa o
JupyterLab, abra outro Ubuntu pelo menu Iniciar, ou uma nova aba no Windows
Terminal, e entre na pasta:

```bash
cd ~/jornada_dados_modelagem_ds
```

**Ao fim da aula.** `make derruba` para os containers e mantém o seu
progresso. Na próxima aula: abra o Docker Desktop, abra o Ubuntu,
`cd ~/jornada_dados_modelagem_ds` e `make subir`.

---

## 🆘 Problemas comuns no Windows

| O que apareceu | O que é | O que fazer |
|---|---|---|
| `make: command not found` | Você está no PowerShell, ou pulou o passo 3 | Abra o terminal do **Ubuntu**. Se já está nele, refaça o passo 3 |
| `Cannot connect to the Docker daemon` | O Docker Desktop está fechado | Abra o Docker Desktop e espere a baleia parar |
| `The command 'docker' could not be found in this WSL 2 distro` | A integração com o WSL está desligada | Passo 2, item 4 |
| `wsl --install` não é reconhecido | Windows desatualizado | Rode o Windows Update e tente de novo |
| Erro de virtualização ao instalar o WSL ou o Docker | A virtualização está desligada no BIOS/UEFI | Ligue *Intel VT-x* ou *AMD-V* (ou *SVM*) no BIOS do computador |
| Tudo muito lento | O repositório está em `/mnt/c/...` | Rode `pwd`. Se o caminho começar com `/mnt/`, clone de novo dentro de `~` (passo 4) |
| `$'\r': command not found` ou `bad interpreter` | Os arquivos foram baixados com final de linha do Windows | Clone de novo **pelo terminal do Ubuntu**, dentro de `~` |
| O computador fica sem memória | O WSL usa, por padrão, até metade da RAM | Feche o que não estiver usando. A trilha roda com 8 GB de RAM |
| `http://localhost:8899` não abre no navegador | O JupyterLab ainda está subindo, ou o Docker foi fechado | `make status`. Espere os 2 containers ficarem `healthy` |
| `ports are not available` ou `address already in use` no `make subir` | Outro programa do Windows usa a porta 8899 ou a 5450 | Abra o arquivo `.env` (`nano .env`), troque `PORTA_JUPYTER=8899` por `PORTA_JUPYTER=8999` (ou `PORTA_POSTGRES=5450` por `5550`), salve com `Ctrl+O`, `Enter`, `Ctrl+X` e rode `make subir` de novo. O endereço passa a ser http://localhost:8999 |
| O JupyterLab abre mas pede *token* ou senha | Você abriu outro Jupyter, o seu do Windows | Confira o endereço: tem que ser a porta **8899** |
| `Permission denied` ao salvar um notebook | O repositório foi clonado com `sudo` ou dentro de `/mnt/c` | Clone de novo, **sem** `sudo`, dentro de `~` (passo 4) |

Não resolveu? Rode `make diagnostico` no terminal do Ubuntu, copie a saída e
mande ao instrutor. Veja também o [FAQ geral](./faq.md).
