-- 02_create_credit_spread.sql
-- Synthetic Bond Risk Lab
-- Creates credit_spread table and loads sample rating → spread mapping.

BEGIN;

DROP TABLE IF EXISTS credit_spread CASCADE;

CREATE TABLE credit_spread (
    rating VARCHAR(10) PRIMARY KEY,     -- e.g., AAA, BBB
    spread_bps NUMERIC(6,2) NOT NULL,   -- basis points (e.g., 150.00 = 1.50%)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO credit_spread (rating, spread_bps) VALUES
('AAA',  50.00),
('AA',   70.00),
('A',    90.00),
('BBB', 150.00),
('BB',  250.00),
('B',   400.00),
('CCC', 800.00);

COMMIT;
