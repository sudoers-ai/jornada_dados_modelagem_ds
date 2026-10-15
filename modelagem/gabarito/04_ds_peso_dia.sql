DROP TABLE IF EXISTS analytics.ds_peso_dia;

CREATE TABLE analytics.ds_peso_dia AS
WITH periodo AS (
    SELECT min(dt_saida)::date AS inicio, max(dt_saida)::date AS fim FROM public.fato_entregas
),
grade AS (
    -- a GRADE: todo dia, para toda transportadora - tendo caminhao ou nao
    SELECT t.sk_tempo, t.data, t.dia_semana, t.is_fim_semana, t.is_feriado,
           tr.sk_transportadora, tr.id AS id_transportadora, tr.nome AS transportadora
    FROM periodo
    JOIN public.dim_tempo t ON t.data BETWEEN periodo.inicio AND periodo.fim
    CROSS JOIN public.dim_transportadora tr
),
diario AS (
    SELECT g.*,
           COALESCE(d.qtd_pedidos, 0)                              AS qtd_pedidos,
           round(COALESCE(d.peso_total_gramas, 0) / 1000.0, 2)     AS peso_kg
    FROM grade g
    LEFT JOIN public.fato_peso_diario d
           ON d.sk_tempo = g.sk_tempo AND d.sk_transportadora = g.sk_transportadora
)
SELECT data,
       id_transportadora,
       transportadora,
       qtd_pedidos,
       peso_kg,
       dia_semana,
       is_fim_semana,
       is_feriado,
       -- o passado da serie, sem olhar para o proprio dia (nem para frente)
       lag(peso_kg, 7) OVER serie                                   AS peso_kg_7_dias_antes,
       round(avg(peso_kg) OVER (serie ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING), 2)
                                                                    AS media_7_dias_anteriores
FROM diario
WINDOW serie AS (PARTITION BY id_transportadora ORDER BY data);

ALTER TABLE analytics.ds_peso_dia ADD PRIMARY KEY (data, id_transportadora);
