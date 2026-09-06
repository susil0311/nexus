-- ============================================================
-- NEXUS PM — Complete Database Schema
-- PostgreSQL 15
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for fuzzy text search

-- ────────────────────────────────────────────────────────────
-- ENUMS
-- ────────────────────────────────────────────────────────────
CREATE TYPE user_role AS ENUM ('supervisor', 'planner', 'pm', 'admin', 'auditor');
CREATE TYPE discipline_type AS ENUM ('civil', 'piping', 'electrical', 'instrumentation', 'hse', 'mechanical', 'general');
CREATE TYPE project_status AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');
CREATE TYPE submission_type AS ENUM ('voice', 'text', 'excel', 'pdf', 'dpr', 'csv');
CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'done', 'failed');
CREATE TYPE match_status AS ENUM ('auto_accepted', 'needs_review', 'flagged_new', 'rejected', 'approved');
CREATE TYPE anomaly_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE anomaly_status AS ENUM ('open', 'investigating', 'resolved', 'false_positive');

-- ────────────────────────────────────────────────────────────
-- USERS & AUTH
-- ────────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    name            VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'supervisor',
    discipline      discipline_type,
    project_id      UUID,  -- default project assignment
    password_hash   TEXT NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);

-- ────────────────────────────────────────────────────────────
-- PROJECTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50) UNIQUE NOT NULL,
    client          VARCHAR(255) DEFAULT 'Oil India Limited',
    location        VARCHAR(255),
    latitude        DECIMAL(10, 7),
    longitude       DECIMAL(10, 7),
    baseline_start  DATE NOT NULL,
    baseline_end    DATE NOT NULL,
    revised_end     DATE,
    status          project_status DEFAULT 'active',
    budget_crore    DECIMAL(15, 2),
    project_manager VARCHAR(255),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Add FK for users.project_id
ALTER TABLE users ADD CONSTRAINT fk_users_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL;

-- ────────────────────────────────────────────────────────────
-- SCHEDULE NODES (WBS — L1 to L6)
-- ────────────────────────────────────────────────────────────
CREATE TABLE schedule_nodes (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    activity_id         VARCHAR(100) NOT NULL,      -- Primavera/MSP native ID
    parent_id           UUID REFERENCES schedule_nodes(id) ON DELETE CASCADE,
    level               SMALLINT NOT NULL CHECK (level BETWEEN 1 AND 6),
    discipline          discipline_type,
    name                VARCHAR(500) NOT NULL,
    description         TEXT,
    baseline_start      DATE,
    baseline_finish     DATE,
    planned_duration    INTEGER,                    -- working days
    planned_quantity    DECIMAL(12, 3),
    unit                VARCHAR(50),               -- m, T, nos, m3, etc.
    resource_code       VARCHAR(100),
    is_milestone        BOOLEAN DEFAULT FALSE,
    float_days          INTEGER DEFAULT 0,
    weight_pct          DECIMAL(5, 2),             -- % contribution to parent
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, activity_id)
);

-- ────────────────────────────────────────────────────────────
-- FIELD SUBMISSIONS (raw inputs from field)
-- ────────────────────────────────────────────────────────────
CREATE TABLE field_submissions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    submitted_by        UUID REFERENCES users(id),
    submission_type     submission_type NOT NULL,
    raw_content         TEXT,
    file_path           VARCHAR(500),
    audio_path          VARCHAR(500),
    transcript          TEXT,
    discipline          discipline_type,
    submission_date     DATE DEFAULT CURRENT_DATE,
    processing_status   processing_status DEFAULT 'pending',
    error_message       TEXT,
    events_extracted    INTEGER DEFAULT 0,
    events_matched      INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- EXTRACTED EVENTS (output of NLP extraction)
-- ────────────────────────────────────────────────────────────
CREATE TABLE extracted_events (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id           UUID REFERENCES field_submissions(id) ON DELETE CASCADE,
    project_id              UUID NOT NULL REFERENCES projects(id),
    raw_description         TEXT NOT NULL,
    discipline              discipline_type,
    extracted_start         DATE,
    extracted_finish        DATE,
    progress_pct            DECIMAL(5, 2) CHECK (progress_pct >= 0),
    quantity_done           DECIMAL(12, 3),
    location_tag            VARCHAR(255),
    supervisor_name         VARCHAR(255),
    extraction_model        VARCHAR(100) DEFAULT 'gemini-1.5-flash',
    extraction_confidence   DECIMAL(5, 4),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- ACTIVITY MATCHES (output of fuzzy/semantic matching)
-- ────────────────────────────────────────────────────────────
CREATE TABLE activity_matches (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extracted_event_id      UUID NOT NULL REFERENCES extracted_events(id) ON DELETE CASCADE,
    schedule_node_id        UUID REFERENCES schedule_nodes(id) ON DELETE SET NULL,
    match_score             DECIMAL(5, 4),
    match_method            VARCHAR(100) DEFAULT 'semantic_embedding',
    match_explanation       TEXT,
    candidate_nodes         JSONB DEFAULT '[]',    -- top-3 candidates stored
    status                  match_status DEFAULT 'needs_review',
    reviewed_by             UUID REFERENCES users(id),
    reviewed_at             TIMESTAMPTZ,
    review_notes            TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- ACTUAL PROGRESS (official actuals after matching/review)
-- ────────────────────────────────────────────────────────────
CREATE TABLE actual_progress (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    schedule_node_id    UUID NOT NULL REFERENCES schedule_nodes(id),
    match_id            UUID REFERENCES activity_matches(id),
    actual_start        DATE,
    actual_finish       DATE,
    progress_pct        DECIMAL(5, 2) CHECK (progress_pct BETWEEN 0 AND 100),
    quantity_done       DECIMAL(12, 3),
    is_complete         BOOLEAN DEFAULT FALSE,
    confidence_score    DECIMAL(5, 4),
    source_type         VARCHAR(50),
    reported_by         UUID REFERENCES users(id),
    audit_hash          VARCHAR(64),               -- SHA-256 for tamper detection
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- PERFORMANCE METRICS (computed, time-series)
-- ────────────────────────────────────────────────────────────
CREATE TABLE performance_metrics (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id              UUID NOT NULL REFERENCES projects(id),
    schedule_node_id        UUID REFERENCES schedule_nodes(id),
    computed_at             TIMESTAMPTZ DEFAULT NOW(),
    spi                     DECIMAL(6, 4),
    cpi                     DECIMAL(6, 4),
    planned_pct             DECIMAL(5, 2),
    actual_pct              DECIMAL(5, 2),
    float_consumed          INTEGER,
    predicted_finish        DATE,
    predicted_delay_days    INTEGER,
    delay_risk_score        DECIMAL(5, 4),
    forecast_explanation    TEXT,
    metadata                JSONB DEFAULT '{}'
);

-- ────────────────────────────────────────────────────────────
-- ANOMALY FLAGS
-- ────────────────────────────────────────────────────────────
CREATE TABLE anomaly_flags (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    related_event_id    UUID REFERENCES extracted_events(id),
    related_match_id    UUID REFERENCES activity_matches(id),
    anomaly_type        VARCHAR(100) NOT NULL,
    description         TEXT NOT NULL,
    severity            anomaly_severity DEFAULT 'medium',
    status              anomaly_status DEFAULT 'open',
    ai_reasoning        TEXT,
    resolved_by         UUID REFERENCES users(id),
    resolved_at         TIMESTAMPTZ,
    resolution_notes    TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- INSTITUTIONAL MEMORY
-- ────────────────────────────────────────────────────────────
CREATE TABLE institutional_memory (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID REFERENCES projects(id) ON DELETE SET NULL,
    project_code        VARCHAR(50),
    project_name        VARCHAR(255),
    discipline          discipline_type,
    activity_type       VARCHAR(255) NOT NULL,
    activity_keywords   TEXT[],
    planned_duration    INTEGER,
    actual_duration     INTEGER,
    productivity_unit   VARCHAR(100),
    planned_quantity    DECIMAL(12, 3),
    actual_quantity     DECIMAL(12, 3),
    delay_days          INTEGER DEFAULT 0,
    delay_causes        TEXT[],
    season              VARCHAR(20),              -- monsoon, summer, winter, dry
    location_type       VARCHAR(100),             -- onshore, offshore, urban, remote
    notes               TEXT,
    tags                TEXT[],
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- AUDIT TRAIL (append-only)
-- ────────────────────────────────────────────────────────────
CREATE TABLE audit_trail (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,
    entity      VARCHAR(100) NOT NULL,
    entity_id   UUID,
    old_value   JSONB,
    new_value   JSONB,
    ip_address  INET,
    user_agent  TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
-- INDEXES
-- ────────────────────────────────────────────────────────────
CREATE INDEX idx_schedule_nodes_project ON schedule_nodes(project_id);
CREATE INDEX idx_schedule_nodes_parent ON schedule_nodes(parent_id);
CREATE INDEX idx_schedule_nodes_discipline ON schedule_nodes(project_id, discipline);
CREATE INDEX idx_schedule_nodes_level ON schedule_nodes(project_id, level);
CREATE INDEX idx_schedule_nodes_name_trgm ON schedule_nodes USING gin(name gin_trgm_ops);

CREATE INDEX idx_field_submissions_project ON field_submissions(project_id, created_at DESC);
CREATE INDEX idx_field_submissions_status ON field_submissions(processing_status);

CREATE INDEX idx_extracted_events_submission ON extracted_events(submission_id);
CREATE INDEX idx_extracted_events_project ON extracted_events(project_id);

CREATE INDEX idx_activity_matches_status ON activity_matches(status);
CREATE INDEX idx_activity_matches_event ON activity_matches(extracted_event_id);

CREATE INDEX idx_actual_progress_node ON actual_progress(schedule_node_id);
CREATE INDEX idx_actual_progress_project ON actual_progress(project_id, created_at DESC);

CREATE INDEX idx_performance_metrics_project ON performance_metrics(project_id, computed_at DESC);

CREATE INDEX idx_anomaly_flags_project ON anomaly_flags(project_id, status, severity);

CREATE INDEX idx_institutional_memory_discipline ON institutional_memory(discipline, activity_type);
CREATE INDEX idx_audit_trail_entity ON audit_trail(entity, entity_id, created_at DESC);

-- ────────────────────────────────────────────────────────────
-- VIEWS
-- ────────────────────────────────────────────────────────────

-- Latest performance metrics per project
CREATE VIEW v_project_latest_metrics AS
SELECT DISTINCT ON (project_id)
    project_id,
    spi,
    cpi,
    planned_pct,
    actual_pct,
    predicted_finish,
    predicted_delay_days,
    delay_risk_score,
    computed_at
FROM performance_metrics
ORDER BY project_id, computed_at DESC;

-- Activity progress summary
CREATE VIEW v_activity_progress AS
SELECT
    sn.id AS node_id,
    sn.project_id,
    sn.activity_id,
    sn.name,
    sn.discipline,
    sn.level,
    sn.baseline_start,
    sn.baseline_finish,
    sn.planned_duration,
    sn.float_days,
    ap.actual_start,
    ap.actual_finish,
    ap.progress_pct,
    ap.is_complete,
    ap.confidence_score,
    CASE
        WHEN ap.is_complete THEN 'complete'
        WHEN ap.actual_start IS NOT NULL AND ap.progress_pct > 0 THEN
            CASE
                WHEN sn.float_days <= 0 THEN 'critical'
                WHEN sn.float_days <= 3 THEN 'at_risk'
                ELSE 'in_progress'
            END
        WHEN sn.baseline_start <= CURRENT_DATE AND ap.actual_start IS NULL THEN 'delayed_start'
        ELSE 'not_started'
    END AS status
FROM schedule_nodes sn
LEFT JOIN actual_progress ap ON ap.schedule_node_id = sn.id
    AND ap.created_at = (
        SELECT MAX(created_at) FROM actual_progress
        WHERE schedule_node_id = sn.id
    );

COMMENT ON TABLE users IS 'Platform users with role-based access';
COMMENT ON TABLE projects IS 'Infrastructure projects (Oil India, EPC, etc.)';
COMMENT ON TABLE schedule_nodes IS 'WBS activity nodes L1-L6 from Primavera/MS Project';
COMMENT ON TABLE field_submissions IS 'Raw field inputs: voice, text, file uploads';
COMMENT ON TABLE extracted_events IS 'Activity events extracted by AI from field submissions';
COMMENT ON TABLE activity_matches IS 'Semantic matches between extracted events and schedule nodes';
COMMENT ON TABLE actual_progress IS 'Official actual progress after match review/approval';
COMMENT ON TABLE institutional_memory IS 'Historical project knowledge for future planning via RAG';
COMMENT ON TABLE audit_trail IS 'Immutable log of all system actions';
