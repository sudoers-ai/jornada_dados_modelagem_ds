DROP TABLE IF EXISTS analytics.ds_entrega;

CREATE TABLE analytics.ds_entrega AS
WITH foto AS (
    SELECT max(dt_venda) AS momento FROM public.fato_pedidos
),
caminhao AS (
    SELECT id_transporte, count(*) AS qtd_pedidos, sum(peso_gramas) AS peso_gramas
    FROM public.fato_entregas
    GROUP BY id_transporte
)
SELECT e.id_transporte,
       e.id_pedido,
       e.dt_saida,
       tr.nome                                                   AS transportadora,
       l.uf                                                      AS uf_destino,
       round(e.peso_gramas / 1000.0, 2)                          AS peso_kg,
       round(c.peso_gramas / 1000.0, 2)                          AS peso_caminhao_kg,
       c.qtd_pedidos::integer                                    AS qtd_pedidos_no_caminhao,
       (e.dt_entrega_prevista::date - e.dt_saida::date)          AS prazo_dias,
       extract(isodow FROM e.dt_saida)::integer                  AS dia_semana_saida,
       -- o historico da transportadora ATE a saida deste caminhao
       (SELECT round(avg(CASE WHEN x.dt_entrega > x.dt_entrega_prevista THEN 1.0 ELSE 0 END), 3)
          FROM public.fato_entregas x
         WHERE x.sk_transportadora = e.sk_transportadora
           AND x.dt_entrega < e.dt_saida)                        AS taxa_atraso_transportadora,
       -- o ROTULO, so para quem ja teve TEMPO de chegar (ou de atrasar)
       CASE WHEN e.dt_saida < foto.momento - interval '10 days'
            THEN e.dt_entrega > e.dt_entrega_prevista END        AS atrasou,
       CASE WHEN e.dt_saida >= foto.momento - interval '10 days' THEN 'sem_rotulo'
            WHEN e.dt_saida <  foto.momento - interval '60 days' THEN 'treino'
            ELSE 'teste' END                                     AS particao
FROM public.fato_entregas e
CROSS JOIN foto
JOIN caminhao c                     ON c.id_transporte = e.id_transporte
JOIN public.dim_transportadora tr   ON tr.sk_transportadora = e.sk_transportadora
JOIN public.dim_localidade l        ON l.sk_localidade = e.sk_localidade;

ALTER TABLE analytics.ds_entrega ADD PRIMARY KEY (id_transporte, id_pedido);
