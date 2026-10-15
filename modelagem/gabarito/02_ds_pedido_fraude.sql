DROP TABLE IF EXISTS analytics.ds_pedido_fraude;

CREATE TABLE analytics.ds_pedido_fraude AS
WITH foto AS (
    -- o dia em que o DW foi fotografado: a referencia de "hoje"
    SELECT max(dt_venda)::date AS dia FROM public.fato_pedidos
),
pedidos AS (
    -- os ITENS viram PEDIDO: agregar antes de juntar, para nao multiplicar linhas
    SELECT f.id_pedido,
           min(f.sk_pessoa)          AS sk_pessoa,
           min(f.dt_venda)           AS dt_venda,
           sum(f.valor_total)        AS valor_total,
           count(*)                  AS qtd_itens,
           sum(f.peso_gramas)        AS peso_gramas,
           min(f.sk_forma_pagamento) AS sk_forma_pagamento,
           min(f.sk_localidade)      AS sk_localidade,
           min(f.sk_dispositivo)     AS sk_dispositivo,
           bool_or(f.is_fraude)      AS is_fraude,
           max(f.dt_fraude)          AS dt_fraude
    FROM public.fato_pedidos f
    GROUP BY f.id_pedido
),
uso_aparelho AS (
    -- quando cada pessoa usou cada aparelho pela primeira vez
    SELECT p.id AS id_pessoa, f.sk_dispositivo, min(f.dt_venda) AS primeiro_uso
    FROM public.fato_pedidos f
    JOIN public.dim_pessoas p ON p.sk_pessoa = f.sk_pessoa
    GROUP BY 1, 2
)
SELECT pd.id_pedido,
       pe.id                                             AS id_pessoa,
       pd.dt_venda,
       pd.valor_total,
       pd.qtd_itens::integer                             AS qtd_itens,
       round(pd.peso_gramas / 1000.0, 2)                 AS peso_kg,
       fp.forma                                          AS forma_pagamento,
       extract(hour FROM pd.dt_venda)::integer           AS hora_venda,
       t.is_fim_semana,
       NOT l.is_area_atendida                            AS is_fora_da_area,
       l.uf <> fs.uf                                     AS is_uf_diferente_do_cadastro,
       -- o aparelho: so o que se sabia ANTES desta compra
       NOT EXISTS (SELECT 1 FROM uso_aparelho u
                   WHERE u.id_pessoa = pe.id AND u.sk_dispositivo = pd.sk_dispositivo
                     AND u.primeiro_uso < pd.dt_venda)   AS is_dispositivo_novo,
       (SELECT count(*) FROM uso_aparelho u
         WHERE u.sk_dispositivo = pd.sk_dispositivo AND u.id_pessoa <> pe.id
           AND u.primeiro_uso < pd.dt_venda)::integer    AS qtd_outras_contas_no_dispositivo,
       -- o cliente: como ele era no inicio do dia da compra (feature table)
       fs.dias_de_cadastro,
       fs.qtd_pedidos_total,
       fs.qtd_pedidos_30d,
       fs.valor_medio_pedido,
       fs.dias_desde_ultimo_pedido,
       fs.qtd_dispositivos,
       round(pd.valor_total / NULLIF(fs.valor_medio_pedido, 0), 2) AS razao_valor_vs_media,
       -- o rotulo, so quando ja esta maduro
       CASE WHEN pd.dt_venda < foto.dia - 7 THEN pd.is_fraude END  AS is_fraude,
       CASE WHEN pd.dt_venda < foto.dia - 60 THEN 'treino'
            WHEN pd.dt_venda < foto.dia - 7  THEN 'teste'
            ELSE 'sem_rotulo' END                                  AS particao
FROM pedidos pd
CROSS JOIN foto
JOIN public.dim_pessoas pe          ON pe.sk_pessoa = pd.sk_pessoa
JOIN public.dim_forma_pagamento fp  ON fp.sk_forma_pagamento = pd.sk_forma_pagamento
JOIN public.dim_localidade l        ON l.sk_localidade = pd.sk_localidade
JOIN public.dim_tempo t             ON t.data = pd.dt_venda::date
JOIN analytics.fs_cliente fs        ON fs.id_pessoa = pe.id AND fs.data = pd.dt_venda::date;

ALTER TABLE analytics.ds_pedido_fraude ADD PRIMARY KEY (id_pedido);
