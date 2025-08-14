CREATE TABLE historia (
    identificacion VARCHAR(64) NOT NULL,
    corte DATE NOT NULL,
    saldo DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (identificacion, corte)
);

CREATE TABLE retiros (
    identificacion VARCHAR(64) NOT NULL PRIMARY KEY,
    fecha_retiro DATE
);

SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Proyectos/Prueba tecnica/historia.csv'
INTO TABLE historia
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(identificacion, @corte, saldo)
SET corte = STR_TO_DATE(@corte, '%d/%m/%Y');


LOAD DATA LOCAL INFILE 'C:/Proyectos/Prueba tecnica/retiros.csv'
INTO TABLE retiros
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(identificacion, @fecha_retiro)
SET fecha_retiro = STR_TO_DATE(
    CONCAT(
        SUBSTRING_INDEX(@fecha_retiro, '-', 1), '-',  -- Día
        CASE SUBSTRING_INDEX(SUBSTRING_INDEX(@fecha_retiro, '-', 2), '-', -1)
            WHEN 'ene' THEN 'jan'
            WHEN 'feb' THEN 'feb'
            WHEN 'mar' THEN 'mar'
            WHEN 'abr' THEN 'apr'
            WHEN 'may' THEN 'may'
            WHEN 'jun' THEN 'jun'
            WHEN 'jul' THEN 'jul'
            WHEN 'ago' THEN 'aug'
            WHEN 'sep' THEN 'sep'
            WHEN 'oct' THEN 'oct'
            WHEN 'nov' THEN 'nov'
            WHEN 'dic' THEN 'dec'
        END, '-',
        SUBSTRING_INDEX(@fecha_retiro, '-', -1)  -- Año
    ),
'%d-%b-%y');
