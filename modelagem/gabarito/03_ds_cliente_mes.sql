DROP TABLE IF EXISTS analytics.ds_cliente_mes;

CREATE TABLE analytics.ds_cliente_mes AS
WITH pedidos AS (
    SELECT p.id AS id_pessoa, c.dt_criado, c.valor_total, c.status_atual
    FROM public.fato_ciclo_pedido c
    JOIN public.dim_pessoas p ON p.sk_pessoa = c.sk_pessoa
),
periodo AS (
    SELECT min(dt_criado)::date AS inicio, max(dt_criado)::date AS fim FROM pedidos
),
meses AS (
    -- so meses COMPLETOS: o DW comeca no meio de um mes e termina no 1o dia de outro
    SELECT m::date AS mes
    FROM periodo,
         generate_series(date_trunc('month', inicio), date_trunc('month', fim), interval '1 month') AS m
    WHERE m::date >= inicio
      AND (m + interval '1 month' - interval '1 day')::date <= fim
),
clientes AS (
    SELECT id AS id_pessoa, min(created_at)::date AS dt_cadastro
    FROM public.dim_pessoas
    GROUP BY id
),
grade AS (
    -- a GRADE: todo cliente, em todo mes em que ja era cliente - comprando ou nao
    SELECT c.id_pessoa, c.dt_cadastro, m.mes
    FROM clientes c
    JOIN meses m ON c.dt_cadastro < m.mes
),
compras AS (
    SELECT id_pessoa, date_trunc('month', dt_criado)::date AS mes,
           count(*) AS qtd_pedidos, sum(valor_total) AS valor_total
    FROM pedidos
    WHERE status_atual NOT IN ('cancelado', 'devolvido')
    GROUP BY 1, 2
),
mensal AS (
    SELECT g.id_pessoa, g.dt_cadastro, g.mes,
           COALESCE(c.qtd_pedidos, 0)::integer AS qtd_pedidos,
           COALESCE(c.valor_total, 0)          AS valor_total
    FROM grade g
    LEFT JOIN compras c ON c.id_pessoa = g.id_pessoa AND c.mes = g.mes
)
SELECT id_pessoa,
       mes,
       qtd_pedidos,
       valor_total,
       ((extract(year FROM mes) - extract(year FROM dt_cadastro)) * 12
         + extract(month FROM mes) - extract(month FROM dt_cadastro))::integer AS meses_de_cliente,
       sum(qtd_pedidos) OVER (PARTITION BY id_pessoa ORDER BY mes
                              ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)::integer AS qtd_pedidos_3m,
       -- o ROTULO: o mes SEGUINTE. Nulo no ultimo mes, porque ainda nao aconteceu
       CASE WHEN lead(mes) OVER (PARTITION BY id_pessoa ORDER BY mes) IS NOT NULL
            THEN lead(qtd_pedidos) OVER (PARTITION BY id_pessoa ORDER BY mes) > 0
       END AS comprou_mes_seguinte
FROM mensal;

ALTER TABLE analytics.ds_cliente_mes ADD PRIMARY KEY (id_pessoa, mes);
