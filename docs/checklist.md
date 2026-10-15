# ✅ Checklist do aluno

> ⬅️ [README principal](../README.md)

Use este checklist para não se perder entre as etapas. Marque cada item
**somente depois de ver a evidência** correspondente. O detalhe de cada
evidência está em [validacao_evidencia.md](./validacao_evidencia.md).

### 0) Preparação do ambiente

* [ ] **Windows:** segui o guia [Preparando o Windows](./windows.md) e estou no terminal do Ubuntu (WSL)
* [ ] Docker e Docker Compose v2 instalados
* [ ] `make --version` mostra a versão do `make`
* [ ] `make verificar` terminou com **Tudo certo**
* [ ] `make subir` terminou com **Tudo no ar**
* [ ] `make status` mostra os 2 containers `healthy`
* [ ] http://localhost:8899 abre o JupyterLab na pasta `notebooks`

### 1) Conhecer o DW

* [ ] Rodei o notebook `01_conhecer_o_dw` inteiro, sem erro
* [ ] Sei o grão das quatro fatos
* [ ] Sei por que juntar com a `dim_pessoas` pelo `id` multiplica linhas
* [ ] Sei por que a fraude da última semana parece menor

### 2) O notebook herdado

* [ ] Vi o AUC de 0,986 no notebook
* [ ] `make avaliar t=legado` mostrou a queda para 0,627 em produção
* [ ] Sei explicar os sete erros
* [ ] `make progresso` mostra a etapa 2 como **investigado**

### 3) Feature table do cliente

* [ ] `make conferir t=fs_cliente` deu ✅ (90.500 linhas)
* [ ] Fiz o "experimente errar" e vi a conferência apontar a coluna

### 4) Tabela de treino

* [ ] `make conferir t=ds_pedido_fraude` deu ✅ (5.000 linhas)
* [ ] `make avaliar t=fraude` mostrou notebook e produção iguais (0,942)

### 5) Painel cliente × mês

* [ ] `make conferir t=ds_cliente_mes` deu ✅ (2.500 linhas)

### 6) Série temporal

* [ ] `make conferir t=ds_peso_dia` deu ✅ (895 linhas)

### 7) Rótulo por regra

* [ ] `make conferir t=ds_entrega` deu ✅ (4.599 linhas)
* [ ] `make progresso` mostra **6 de 6**

### 8) Desafios

* [ ] Escolhi o meu nível em [desafios/desafios.md](../desafios/desafios.md)
* [ ] Entregáveis prontos

### Ao fim de cada aula

* [ ] Salvei os notebooks no JupyterLab (`Ctrl + S`)
* [ ] `make derruba` (para os containers e **mantém** o seu progresso)
