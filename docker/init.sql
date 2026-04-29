-- ─────────────────────────────────────────────────────────────────
-- Threat Intelligence Pipeline — Database Schema
-- ─────────────────────────────────────────────────────────────────

-- ── Extensions ────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for fuzzy text search

-- ── IoCs table ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS iocs (
    id            BIGSERIAL    PRIMARY KEY,
    event_id      UUID         NOT NULL DEFAULT uuid_generate_v4(),
    ioc_type      VARCHAR(16)  NOT NULL CHECK (ioc_type IN ('ip', 'domain', 'hash', 'url')),
    ioc_value     TEXT         NOT NULL,
    source        VARCHAR(64),
    confidence    REAL         CHECK (confidence BETWEEN 0 AND 1),
    tags          TEXT[]       DEFAULT '{}',

    -- Geo
    country_code  CHAR(2),
    country_name  VARCHAR(100),
    city          VARCHAR(100),
    latitude      REAL,
    longitude     REAL,

    -- ASN
    asn           VARCHAR(20),
    isp           VARCHAR(200),
    org           VARCHAR(200),

    -- Reputation
    abuse_score   SMALLINT     CHECK (abuse_score BETWEEN 0 AND 100),
    vt_detections SMALLINT,
    vt_total      SMALLINT,
    is_tor        BOOLEAN      DEFAULT FALSE,
    is_vpn        BOOLEAN      DEFAULT FALSE,
    is_datacenter BOOLEAN      DEFAULT FALSE,

    -- ML scoring
    risk_score    REAL         CHECK (risk_score BETWEEN 0 AND 100),
    risk_level    VARCHAR(16)  CHECK (risk_level IN ('CRITICAL','HIGH','MEDIUM','LOW','INFO')),

    -- Timestamps
    ingested_at   BIGINT       NOT NULL,
    enriched_at   BIGINT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Alerts table ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id          BIGSERIAL    PRIMARY KEY,
    alert_id    UUID         NOT NULL DEFAULT uuid_generate_v4(),
    event_id    UUID         NOT NULL,
    ioc_value   TEXT         NOT NULL,
    ioc_type    VARCHAR(16)  NOT NULL,
    risk_level  VARCHAR(16)  NOT NULL,
    risk_score  REAL         NOT NULL,
    rule_name   VARCHAR(100),
    description TEXT,
    country_code CHAR(2),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Users table ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id           BIGSERIAL   PRIMARY KEY,
    email        VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role         VARCHAR(20) NOT NULL DEFAULT 'analyst',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_iocs_event_id   ON iocs (event_id);
CREATE INDEX IF NOT EXISTS idx_iocs_ioc_value  ON iocs USING gin (ioc_value gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_iocs_risk_level ON iocs (risk_level);
CREATE INDEX IF NOT EXISTS idx_iocs_ioc_type   ON iocs (ioc_type);
CREATE INDEX IF NOT EXISTS idx_iocs_created_at ON iocs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iocs_country    ON iocs (country_code);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_risk_level  ON alerts (risk_level);

-- ── Seed admin user (password: changeme) ─────────────────────────
INSERT INTO users (email, password_hash, role)
VALUES (
    'admin@threatintel.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN3b9NevGkVKAGLQ5Wq2K', -- bcrypt of "changeme"
    'admin'
) ON CONFLICT (email) DO NOTHING;
