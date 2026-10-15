DROP TABLE IF EXISTS analytics.fs_cliente;

CREATE TABLE analytics.fs_cliente AS
WITH pedidos AS (
    -- 1 linha por pedido: a fato_ciclo_pedido ja esta neste grao
    SELECT c.id_pedido, p.id AS id_pessoa, c.dt_criado, c.valor_total
    FROM public.fato_ciclo_pedido c
    JOIN public.dim_pessoas p ON p.sk_pessoa = c.sk_pessoa
),
periodo AS (
    SELECT min(dt_criado)::date AS inicio, max(dt_criado)::date AS fim FROM pedidos
),
clientes AS (
    SELECT id AS id_pessoa, min(created_at)::date AS dt_cadastro
    FROM public.dim_pessoas
    GROUP BY id
),
grade AS (
    -- a GRADE: uma linha por cliente por dia, desde o cadastro, sem buracos
    SELECT c.id_pessoa, c.dt_cadastro, t.data
    FROM clientes c
    CROSS JOIN periodo
    JOIN public.dim_tempo t
      ON t.data BETWEEN GREATEST(c.dt_cadastro, periodo.inicio) AND periodo.fim
),
pedidos_dia AS (
    SELECT id_pessoa, dt_criado::date AS data, count(*) AS qtd, sum(valor_total) AS valor
    FROM pedidos
    GROUP BY 1, 2
),
aparelhos_dia AS (
    -- o dia em que a pessoa usou cada aparelho pela PRIMEIRA vez
    SELECT id_pessoa, primeiro_uso::date AS data, count(*) AS novos
    FROM (
        SELECT p.id AS id_pessoa, f.sk_dispositivo, min(f.dt_venda) AS primeiro_uso
        FROM public.fato_pedidos f
        JOIN public.dim_pessoas p ON p.sk_pessoa = f.sk_pessoa
        GROUP BY 1, 2
    ) primeiro
    GROUP BY 1, 2
),
diario AS (
    SELECT g.id_pessoa, g.dt_cadastro, g.data,
           COALESCE(pd.qtd, 0)    AS qtd,
           COALESCE(pd.valor, 0)  AS valor,
           COALESCE(ad.novos, 0)  AS novos
    FROM grade g
    LEFT JOIN pedidos_dia pd   ON pd.id_pessoa = g.id_pessoa AND pd.data = g.data
    LEFT JOIN aparelhos_dia ad ON ad.id_pessoa = g.id_pessoa AND ad.data = g.data
)
SELECT d.id_pessoa,
       d.data,
       v.uf,                                                       -- a UF que valia NAQUELE dia (SCD 2)
       d.data - d.dt_cadastro                                      AS dias_de_cadastro,
       COALESCE(sum(d.qtd) OVER ate_ontem, 0)::integer             AS qtd_pedidos_total,
       COALESCE(sum(d.qtd) OVER ultimos_30, 0)::integer            AS qtd_pedidos_30d,
       round(sum(d.valor) OVER ate_ontem
             / NULLIF(sum(d.qtd) OVER ate_ontem, 0), 2)            AS valor_medio_pedido,
       d.data - max(CASE WHEN d.qtd > 0 THEN d.data END) OVER ate_ontem
                                                                   AS dias_desde_ultimo_pedido,
       COALESCE(sum(d.novos) OVER ate_ontem, 0)::integer           AS qtd_dispositivos
FROM diario d
JOIN public.dim_pessoas v
  ON v.id = d.id_pessoa
 AND d.data::timestamp >= v.dt_inicio
 AND d.data::timestamp <  COALESCE(v.dt_fim, 'infinity')
WINDOW ate_ontem  AS (PARTITION BY d.id_pessoa ORDER BY d.data
                      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING),
       ultimos_30 AS (PARTITION BY d.id_pessoa ORDER BY d.data
                      ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING);

ALTER TABLE analytics.fs_cliente ADD PRIMARY KEY (id_pessoa, data);
