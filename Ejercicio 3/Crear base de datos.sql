CREATE DATABASE IF NOT EXISTS rachas_db CHARACTER SET utf8mb4;
USE rachas_db;
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
