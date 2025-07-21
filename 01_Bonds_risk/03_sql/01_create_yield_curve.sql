-- 01_create_yield_curve.sql
-- Synthetic Bond Risk Lab
-- Creates yield_curve table and loads 5 sample historical curves.

BEGIN;

-- Drop & recreate (idempotent dev workflow)
DROP TABLE IF EXISTS yield_curve CASCADE;

CREATE TABLE yield_curve (
    curve_id SERIAL PRIMARY KEY,
    curve_date DATE NOT NULL,
    tenor INTERVAL NOT NULL,          -- e.g., '1 year', '5 years'
    yield NUMERIC(6,4) NOT NULL,      -- decimal form: 0.0310 = 3.10%
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample synthetic curves
INSERT INTO yield_curve (curve_date, tenor, yield) VALUES
('2025-07-01', '1 year', 0.0310),
('2025-07-01', '2 years', 0.0320),
('2025-07-01', '5 years', 0.0345),
('2025-07-01', '10 years', 0.0360),
('2025-07-01', '30 years', 0.0375),

('2025-07-05', '1 year', 0.0312),
('2025-07-05', '2 years', 0.0325),
('2025-07-05', '5 years', 0.0348),
('2025-07-05', '10 years', 0.0362),
('2025-07-05', '30 years', 0.0380),

('2025-07-10', '1 year', 0.0305),
('2025-07-10', '2 years', 0.0318),
('2025-07-10', '5 years', 0.0340),
('2025-07-10', '10 years', 0.0355),
('2025-07-10', '30 years', 0.0370),

('2025-07-15', '1 year', 0.0300),
('2025-07-15', '2 years', 0.0312),
('2025-07-15', '5 years', 0.0338),
('2025-07-15', '10 years', 0.0352),
('2025-07-15', '30 years', 0.0365),

('2025-07-20', '1 year', 0.0298),
('2025-07-20', '2 years', 0.0310),
('2025-07-20', '5 years', 0.0335),
('2025-07-20', '10 years', 0.0350),
('2025-07-20', '30 years', 0.0360);

COMMIT;
