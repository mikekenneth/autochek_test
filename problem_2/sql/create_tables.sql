DROP DATABASE IF EXISTS autochek_db;
CREATE DATABASE autochek_db;

\c autochek_db;

--------------------------------- Xe Currencies Table ---------------------------------
CREATE TABLE IF NOT EXISTS xe_currency_exchanges_rates (
	id serial primary key,
	date_key date DEFAULT NOW(),
    "timestamp" TIMESTAMP DEFAULT NOW(),
    currency_from VARCHAR(10),
    usd_to_currency_rate numeric,
    currency_to_usd_rate numeric,
    currency_to VARCHAR(10),
    CONSTRAINT unique_date_currency_to UNIQUE (date_key, currency_to)
); 
