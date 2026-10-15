# 🏗️ Carga — de onde vem o Data Warehouse

> ⬅️ [README principal](../README.md)

Você não precisa rodar nada desta pasta: o `make subir` faz tudo na primeira
vez. Ela está aqui para quem quiser entender como o DW que você recebe foi
construído.

## O caminho dos dados

```text
gerador/            →  banco liga_sudoers      →  carga/etl/        →  banco liga_sudoers_dw
(o universo              (o transacional,           (o ETL em SQL,        (o DW em star schema,
 simulado, com            13 tabelas)                13 passos)            schema public)
 semente fixa)
```

| Arquivo | Papel |
|---|---|
| `carregar.sh` | o roteiro inteiro: cria os bancos, o transacional, o histórico, o DW e roda o ETL. Se o DW já está carregado, não faz nada |
| `ddl/00` a `ddl/03` | cria o transacional e o cadastro base |
| `carregar_historico.py` | grava 180 dias de pedidos no transacional, terminando sempre em **1º de setembro de 2026** |
| `ddl/04` e `ddl/05` | cria o DW (o mesmo da disciplina de modelagem para engenheiros, mais `fato_pedidos.dt_fraude`) |
| `etl/00` a `etl/12` | o ETL: lê o transacional e preenche dimensões e fatos |
| `exportar_base.py` | gera o `ddl/02_oltp_dados_base.sql`. Só para quem mantém o repositório |

## O gerador

A pasta [`gerador/`](../gerador/) tem o universo da Liga Sudoers:

| Arquivo | Papel |
|---|---|
| `liga_sudoers_gen.py` | o gerador canônico da Jornada: pessoas, produtos, pedidos e as fraudes plantadas. É uma **cópia** do arquivo de mesmo nome dos outros repositórios |
| `extensao_modelagem.py` | peso dos produtos, endereços, pagamentos, situações do pedido, transportadoras e transportes |
| `ruido_ds.py` | o que esta disciplina acrescenta para o problema de fraude ficar realista: clientes que viajam, clientes que trocam de celular, um tipo novo de fraude (cartão clonado) e fraudes que nunca são descobertas |

## Por que os números são sempre os mesmos

O gerador é **determinístico** (semente 42), e a foto do DW é **fixa**: as
datas não são deslocadas para "hoje". Por isso todo aluno, em qualquer dia,
vê os mesmos 5.000 pedidos, e os roteiros podem mostrar a saída exata.

## Recomeçar do zero

```bash
make carregar args=--limpar
```

Apaga o transacional, o DW **e as suas tabelas** (`analytics`, `legado`) e
carrega tudo de novo. Os notebooks não são apagados.
