-- =============================================================
--  CALL CENTER + CRM — Database schema
--  Engine : PostgreSQL 14+
--  Author : ErpCallCenter
--  Date   : 2026-11-10
-- =============================================================
--
--  USAGE:
--    1. Create the database manually (or uncomment the
--       CREATE DATABASE statement below) and connect to it.
--    2. Run this file:
--         psql -U postgres -d call_center_db -f schema.sql
--
-- =============================================================

-- -------------------------------------------------------------
--  Optional: create the database
--  (uncomment when running as superuser)
-- -------------------------------------------------------------
-- CREATE DATABASE call_center_db
--     WITH
--     ENCODING    = 'UTF8'
--     LC_COLLATE  = 'en_US.UTF-8'
--     LC_CTYPE    = 'en_US.UTF-8'
--     TEMPLATE    = template0;

-- \connect call_center_db


-- =============================================================
--  CLEANUP (useful when re-running in development)
-- =============================================================
DROP TABLE IF EXISTS predictions   CASCADE;
DROP TABLE IF EXISTS follow_ups   CASCADE;
DROP TABLE IF EXISTS calls       CASCADE;
DROP TABLE IF EXISTS customers       CASCADE;


-- =============================================================
--  ENUM TYPES
-- =============================================================

-- Customer status
DO $$ BEGIN
    CREATE TYPE customer_status_t AS ENUM (
        'New', 'Active', 'Inactive', 'VIP'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Call outcome
DO $$ BEGIN
    CREATE TYPE call_outcome_t AS ENUM (
        'Interested',
        'Not interested',
        'No answer',
        'Busy',
        'Wrong number'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Interest level
DO $$ BEGIN
    CREATE TYPE interest_level_t AS ENUM (
        'High', 'Medium', 'Low', 'No interest'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Follow-up status
DO $$ BEGIN
    CREATE TYPE followup_status_t AS ENUM (
        'Pending', 'Completed', 'Cancelled'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ML prediction classification
DO $$ BEGIN
    CREATE TYPE ml_class_t AS ENUM (
        'High', 'Medium', 'Low'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- =============================================================
--  TABLE: customers
-- =============================================================
CREATE TABLE customers (
    id              SERIAL          PRIMARY KEY,
    name          VARCHAR(100)    NOT NULL,
    phone        VARCHAR(20)     NOT NULL,
    email           VARCHAR(150)    UNIQUE,
    company         VARCHAR(100),
    age            SMALLINT        CHECK (age BETWEEN 18 AND 100),
    registered_at  DATE            NOT NULL DEFAULT CURRENT_DATE,
    status          customer_status_t NOT NULL DEFAULT 'New',

    -- Audit
    created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  customers             IS 'Customers registered in the CRM';
COMMENT ON COLUMN customers.status      IS 'New | Active | Inactive | VIP';
COMMENT ON COLUMN customers.phone    IS 'Free format; e.g. 999123456';


-- =============================================================
--  TABLE: calls
-- =============================================================
CREATE TABLE calls (
    id                      SERIAL              PRIMARY KEY,
    customer_id              INTEGER             NOT NULL
                                REFERENCES customers(id)
                                ON DELETE CASCADE,

    called_at                   TIMESTAMP           NOT NULL DEFAULT NOW(),
    duration_seconds       INTEGER             NOT NULL
                                CHECK (duration_seconds >= 0),

    outcome               call_outcome_t NOT NULL,
    interest                 interest_level_t     NOT NULL DEFAULT 'No interest',
    requested_info    BOOLEAN             NOT NULL DEFAULT FALSE,
    accepted_followup      BOOLEAN             NOT NULL DEFAULT FALSE,
    notes                   TEXT,

    -- Audit
    created_at               TIMESTAMP           NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  calls                      IS 'Record of each call (real or simulated)';
COMMENT ON COLUMN calls.duration_seconds    IS 'Total duration in seconds';
COMMENT ON COLUMN calls.requested_info IS 'Customer asked for more information';
COMMENT ON COLUMN calls.accepted_followup   IS 'Customer agreed to be contacted again';


-- =============================================================
--  TABLE: follow_ups
-- =============================================================
CREATE TABLE follow_ups (
    id                  SERIAL                  PRIMARY KEY,
    customer_id          INTEGER                 NOT NULL
                            REFERENCES customers(id)
                            ON DELETE CASCADE,
    call_id          INTEGER
                            REFERENCES calls(id)
                            ON DELETE SET NULL,

    scheduled_date    DATE                    NOT NULL,
    reason              VARCHAR(200),
    status              followup_status_t    NOT NULL DEFAULT 'Pending',

    -- Audit
    created_at           TIMESTAMP               NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP               NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  follow_ups              IS 'Scheduled commercial follow-ups';
COMMENT ON COLUMN follow_ups.call_id   IS 'Call that originated the follow-up (nullable)';


-- =============================================================
--  TABLE: predictions
-- =============================================================
CREATE TABLE predictions (
    id                  SERIAL              PRIMARY KEY,
    customer_id          INTEGER             NOT NULL
                            REFERENCES customers(id)
                            ON DELETE CASCADE,
    call_id          INTEGER
                            REFERENCES calls(id)
                            ON DELETE SET NULL,

    probability        NUMERIC(5,4)        NOT NULL
                            CHECK (probability BETWEEN 0 AND 1),
    classification       ml_class_t  NOT NULL,
    recommendation       VARCHAR(200),
    predicted_at    TIMESTAMP           NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  predictions              IS 'ML model prediction results';
COMMENT ON COLUMN predictions.probability IS 'Value between 0.0000 and 1.0000';
COMMENT ON COLUMN predictions.classification IS 'High (>=0.65) | Medium (0.35-0.65) | Low (<0.35)';


-- =============================================================
--  INDEXES (performance for frequent queries)
-- =============================================================

-- Clientes
CREATE INDEX idx_customers_status    ON customers  (status);
CREATE INDEX idx_customers_company   ON customers  (company);

-- Llamadas
CREATE INDEX idx_calls_customer   ON calls  (customer_id);
CREATE INDEX idx_calls_called_at     ON calls  (called_at DESC);
CREATE INDEX idx_calls_outcome ON calls  (outcome);

-- Seguimientos
CREATE INDEX idx_fu_customer        ON follow_ups (customer_id);
CREATE INDEX idx_fu_date          ON follow_ups (scheduled_date);
CREATE INDEX idx_fu_status         ON follow_ups (status);

-- Predicciones
CREATE INDEX idx_pred_customer       ON predictions (customer_id);
CREATE INDEX idx_pred_date         ON predictions (predicted_at DESC);
CREATE INDEX idx_pred_class        ON predictions (classification);


-- =============================================================
--  FUNCTION + TRIGGER: update 'updated_at' automatically
-- =============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customers_updated
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_follow_ups_updated
    BEFORE UPDATE ON follow_ups
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================
--  VIEWS for the dashboard
-- =============================================================

-- Call summary per customer
CREATE OR REPLACE VIEW v_customer_summary AS
SELECT
    c.id,
    c.name,
    c.company,
    c.status,
    COUNT(l.id)                                     AS total_calls,
    COALESCE(AVG(l.duration_seconds), 0)::INT      AS avg_duration_sec,
    COUNT(l.id) FILTER (WHERE l.outcome = 'Interested') AS interested_calls,
    MAX(p.probability)                             AS max_conversion_prob,
    MAX(p.classification::TEXT)                      AS best_classification
FROM customers c
LEFT JOIN calls    l ON l.customer_id = c.id
LEFT JOIN predictions p ON p.customer_id = c.id
GROUP BY c.id, c.name, c.company, c.status;

COMMENT ON VIEW v_customer_summary IS 'Per-customer aggregated view for the CRM';


-- Pending follow-ups with customer data
CREATE OR REPLACE VIEW v_pending_followups AS
SELECT
    s.id                AS followup_id,
    s.scheduled_date,
    s.reason,
    s.status,
    c.name            AS customer_name,
    c.phone,
    c.company,
    p.probability,
    p.classification     AS ml_priority
FROM follow_ups s
JOIN customers c     ON c.id = s.customer_id
LEFT JOIN predictions p
    ON p.call_id = s.call_id
WHERE s.status = 'Pending'
ORDER BY p.probability DESC NULLS LAST, s.scheduled_date ASC;

COMMENT ON VIEW v_pending_followups IS 'Pending follow-ups ordered by ML priority';


-- General metrics (for the Dashboard)
CREATE OR REPLACE VIEW v_dashboard_metrics AS
SELECT
    COUNT(*)                                            AS total_calls,
    COUNT(*) FILTER (WHERE outcome = 'Interested')    AS answered_calls,
    COUNT(*) FILTER (WHERE requested_info = TRUE) AS info_requests,
    COUNT(*) FILTER (WHERE accepted_followup   = TRUE) AS accepted_followups,
    AVG(duration_seconds)::INT                         AS avg_duration_sec,
    (SELECT COUNT(*) FROM follow_ups WHERE status = 'Pending')  AS pending_followups,
    (SELECT COUNT(*) FROM customers)                                 AS total_customers,
    (SELECT COUNT(*) FROM predictions WHERE classification = 'High') AS high_predictions
FROM calls;

COMMENT ON VIEW v_dashboard_metrics IS 'KPIs for the main dashboard';


-- =============================================================
--  DEMO SEED DATA
--  (10 customers + 5 sample calls to start the demo)
--  The 10,000-row dataset is loaded separately (see data/).
-- =============================================================

INSERT INTO customers (name, phone, email, company, age, registered_at, status) VALUES
    ('María García',     '999111001', 'maria.garcia@email.com',     'TechCorp SA',       34, '2025-01-15', 'Active'),
    ('Carlos López',     '999111002', 'carlos.lopez@email.com',     'Innova SRL',        45, '2025-02-20', 'VIP'),
    ('Ana Martínez',     '999111003', 'ana.martinez@email.com',     'GlobalTech',        28, '2025-03-10', 'New'),
    ('Luis Rodríguez',   '999111004', 'luis.rodriguez@email.com',   'DataSystems',       52, '2025-04-05', 'Active'),
    ('Laura Hernández',  '999111005', 'laura.hernandez@email.com',  'FutureBiz',         31, '2025-05-18', 'New'),
    ('Jorge Pérez',      '999111006', 'jorge.perez@email.com',      'MegaVentas',        40, '2025-06-22', 'Inactive'),
    ('Sofía González',   '999111007', 'sofia.gonzalez@email.com',   'ProSoluciones',     26, '2025-07-14', 'Active'),
    ('Miguel Torres',    '999111008', 'miguel.torres@email.com',    'AlphaGroup',        37, '2025-08-30', 'VIP'),
    ('Valentina Díaz',   '999111009', 'valentina.diaz@email.com',   'BetaServices',      29, '2025-09-12', 'New'),
    ('Andrés Flores',    '999111010', 'andres.flores@email.com',    'NexusComercial',    48, '2025-10-07', 'Active');

INSERT INTO calls (customer_id, called_at, duration_seconds, outcome, interest, requested_info, accepted_followup, notes) VALUES
    (1, '2026-10-01 09:15:00', 320, 'Interested',     'High',        TRUE,  TRUE,  'Very receptive customer, ready to buy'),
    (2, '2026-10-02 10:30:00', 540, 'Interested',     'High',        TRUE,  TRUE,  'Asked for a formal proposal'),
    (3, '2026-10-03 11:00:00', 120, 'Not interested', 'Low',         FALSE, FALSE, 'No interest at this time'),
    (4, '2026-10-04 14:00:00', 290, 'Interested',     'Medium',      TRUE,  FALSE, 'Comparing with competitors'),
    (5, '2026-10-05 16:45:00',  60, 'No answer',      'No interest', FALSE, FALSE, NULL);

INSERT INTO follow_ups (customer_id, call_id, scheduled_date, reason, status) VALUES
    (1, 1, '2026-11-13', 'Deal closing',         'Pending'),
    (2, 2, '2026-11-14', 'Proposal delivery',    'Pending'),
    (4, 4, '2026-11-15', 'Commercial follow-up', 'Pending');

INSERT INTO predictions (customer_id, call_id, probability, classification, recommendation) VALUES
    (1, 1, 0.8700, 'High',   'Prioritize immediate follow-up'),
    (2, 2, 0.7900, 'High',   'Prioritize immediate follow-up'),
    (3, 3, 0.1200, 'Low',    'Do not prioritize in this campaign'),
    (4, 4, 0.5500, 'Medium', 'Schedule follow-up in 7 days');


-- =============================================================
--  END OF SCHEMA
-- =============================================================
