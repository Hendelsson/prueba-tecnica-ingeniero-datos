-- Definir variables de parámetros
SET @fecha_base = '2024-06-30';  -- Fecha de referencia (puedes cambiarla)
SET @n = 3;                      -- Número mínimo de meses consecutivos en la racha

-- 1. Normalizar los datos: crear una lista de todos los meses entre el primer y el último corte hasta fecha_base
WITH RECURSIVE meses AS (
    SELECT DATE_FORMAT(MIN(corte), '%Y-%m-01') AS mes
    FROM historia
    UNION ALL
    SELECT DATE_ADD(mes, INTERVAL 1 MONTH)
    FROM meses
    WHERE mes < DATE_FORMAT(@fecha_base, '%Y-%m-01')
),

-- 2. Obtener todos los clientes y todos los meses posibles
clientes_meses AS (
    SELECT h.identificacion, m.mes
    FROM (SELECT DISTINCT identificacion FROM historia) h
    CROSS JOIN meses m
),

-- 3. Incorporar los saldos y ajustar las reglas:
--    Si no hay saldo en un mes, saldo = 0 (N0)
--    Si mes > fecha_retiro, no incluir
historia_completa AS (
    SELECT
        cm.identificacion,
        cm.mes,
        COALESCE(h.saldo, 0) AS saldo
    FROM clientes_meses cm
    LEFT JOIN historia h
        ON cm.identificacion = h.identificacion
       AND DATE_FORMAT(h.corte, '%Y-%m-01') = cm.mes
    LEFT JOIN retiros r
        ON cm.identificacion = r.identificacion
    WHERE r.fecha_retiro IS NULL OR cm.mes <= DATE_FORMAT(r.fecha_retiro, '%Y-%m-01')
),

-- 4. Clasificar por nivel de deuda
niveles AS (
    SELECT
        identificacion,
        mes,
        CASE
            WHEN saldo >= 0 AND saldo < 300000 THEN 'N0'
            WHEN saldo >= 300000 AND saldo < 1000000 THEN 'N1'
            WHEN saldo >= 1000000 AND saldo < 3000000 THEN 'N2'
            WHEN saldo >= 3000000 AND saldo < 5000000 THEN 'N3'
            WHEN saldo >= 5000000 THEN 'N4'
        END AS nivel
    FROM historia_completa
),

-- 5. Detectar rachas consecutivas en un mismo nivel
--    Utilizamos la técnica de "gaps and islands" para agrupar meses consecutivos con el mismo nivel
agrupado AS (
    SELECT
        identificacion,
        nivel,
        mes,
        DATE_SUB(mes, INTERVAL ROW_NUMBER() OVER (PARTITION BY identificacion, nivel ORDER BY mes) MONTH) AS grupo
    FROM niveles
),

-- 6. Agrupar por cliente, nivel y grupo para calcular tamaño de racha
rachas AS (
    SELECT
        identificacion,
        nivel,
        MIN(mes) AS fecha_inicio,
        MAX(mes) AS fecha_fin,
        COUNT(*) AS racha
    FROM agrupado
    GROUP BY identificacion, nivel, grupo
),

-- 7. Filtrar rachas que cumplan con el mínimo y estén antes o en la fecha_base
filtradas AS (
    SELECT *
    FROM rachas
    WHERE racha >= @n
      AND fecha_fin <= @fecha_base
),

-- 8. De cada cliente, seleccionar la racha más larga; si hay empate, la más reciente
ordenadas AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY identificacion ORDER BY racha DESC, fecha_fin DESC) AS rn
    FROM filtradas
)

-- 9. Resultado final
SELECT
    identificacion,
    racha,
    fecha_fin,
    nivel
FROM ordenadas
WHERE rn = 1
ORDER BY identificacion;
