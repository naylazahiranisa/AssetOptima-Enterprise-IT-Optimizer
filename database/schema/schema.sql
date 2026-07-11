-- ============================================================================
-- AssetOptima - Enterprise IT Asset & License Optimizer
-- PostgreSQL 17+ Production Schema
--
-- File: schema.sql
-- Description: Complete database schema including ENUMs, tables, indexes,
--              triggers, and views.
-- Author: Principal Database Architect
-- ============================================================================

-- ############################################################################
-- 1. ENUM TYPES
-- ############################################################################

CREATE TYPE employment_status AS ENUM (
    'active',
    'notice',
    'offboarding',
    'inactive'
);

CREATE TYPE employment_type AS ENUM (
    'full_time',
    'part_time',
    'contractor',
    'intern'
);

CREATE TYPE asset_status AS ENUM (
    'available',
    'assigned',
    'maintenance',
    'retired',
    'lost',
    'stolen'
);

CREATE TYPE asset_condition AS ENUM (
    'new',
    'good',
    'fair',
    'poor',
    'damaged',
    'repairing'
);

CREATE TYPE asset_event_type AS ENUM (
    'assigned',
    'returned',
    'transferred',
    'status_changed',
    'maintenance',
    'retired',
    'lost',
    'found',
    'inventory_verified',
    'specs_updated'
);

CREATE TYPE license_type AS ENUM (
    'perpetual',
    'subscription',
    'concurrent',
    'trial',
    'enterprise_agreement'
);

CREATE TYPE license_model AS ENUM (
    'per_seat',
    'per_user',
    'concurrent',
    'enterprise',
    'open_source',
    'free',
    'other'
);

CREATE TYPE location_type AS ENUM (
    'office',
    'warehouse',
    'datacenter',
    'remote',
    'other'
);

CREATE TYPE notification_type AS ENUM (
    'license_expiry',
    'dormant_account',
    'asset_overdue',
    'offboarding',
    'maintenance_due',
    'system',
    'prediction',
    'recommendation'
);

CREATE TYPE notification_severity AS ENUM (
    'info',
    'warning',
    'critical'
);

CREATE TYPE prediction_type AS ENUM (
    'license_forecast',
    'dormant_detection',
    'usage_forecast',
    'cost_forecast'
);

CREATE TYPE recommendation_type AS ENUM (
    'license_reduce',
    'license_increase',
    'revoke_dormant',
    'audit_alert',
    'cost_saving',
    'process_improvement'
);

CREATE TYPE recommendation_status AS ENUM (
    'pending',
    'dismissed',
    'applied',
    'in_progress'
);

CREATE TYPE chat_role AS ENUM (
    'user',
    'assistant',
    'system'
);

CREATE TYPE usage_source AS ENUM (
    'system',
    'api',
    'import',
    'manual'
);

CREATE TYPE setting_value_type AS ENUM (
    'string',
    'integer',
    'boolean',
    'json',
    'float'
);

-- ############################################################################
-- 2. EXTENSION LOADING
-- ############################################################################

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ############################################################################
-- 3. TABLE DEFINITIONS
-- ############################################################################

-- ---------------------------------------------------------------------------
-- 3.1  companies
-- ---------------------------------------------------------------------------
CREATE TABLE companies (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    tax_id              VARCHAR(100),
    address             TEXT,
    phone               VARCHAR(50),
    email               VARCHAR(255),
    website             VARCHAR(255),
    logo_url            VARCHAR(500),
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    max_employees       INTEGER     NOT NULL DEFAULT 0 CHECK (max_employees >= 0),
    subscription_plan   VARCHAR(50) NOT NULL DEFAULT 'free',
    settings            JSONB       DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_companies_code UNIQUE (code),
    CONSTRAINT uq_companies_name UNIQUE (name)
);

COMMENT ON TABLE companies IS 'Tenant organization — all data is scoped to a company';
COMMENT ON COLUMN companies.code IS 'Short tenant code (e.g., ACME) — immutable after creation';
COMMENT ON COLUMN companies.max_employees IS 'License limit for the subscription plan';

-- ---------------------------------------------------------------------------
-- 3.2  roles
-- ---------------------------------------------------------------------------
CREATE TABLE roles (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    description         TEXT,
    priority            INTEGER     NOT NULL DEFAULT 0 CHECK (priority >= 0),
    is_system           BOOLEAN     NOT NULL DEFAULT FALSE,
    permissions         JSONB       NOT NULL DEFAULT '[]',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_roles_company_code UNIQUE (company_id, code)
);

COMMENT ON TABLE roles IS 'Access control role definitions per company';
COMMENT ON COLUMN roles.is_system IS 'System roles (super_admin, it_manager, it_support) cannot be deleted';

-- ---------------------------------------------------------------------------
-- 3.3  users
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id              UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    role_id                 UUID        NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    employee_id             UUID        UNIQUE,
    email                   VARCHAR(255) NOT NULL,
    password_hash           VARCHAR(255) NOT NULL,
    display_name            VARCHAR(255) NOT NULL,
    avatar_url              VARCHAR(500),
    is_active               BOOLEAN     NOT NULL DEFAULT TRUE,
    is_locked               BOOLEAN     NOT NULL DEFAULT FALSE,
    failed_login_attempts   INTEGER     NOT NULL DEFAULT 0 CHECK (failed_login_attempts >= 0),
    last_login_at           TIMESTAMPTZ,
    last_login_ip           VARCHAR(45),
    password_changed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mfa_enabled             BOOLEAN     NOT NULL DEFAULT FALSE,
    mfa_secret              VARCHAR(255),
    refresh_token           TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by              UUID,
    updated_by              UUID,
    deleted_at              TIMESTAMPTZ,
    CONSTRAINT uq_users_email_company UNIQUE (company_id, email)
);

COMMENT ON TABLE users IS 'System users who authenticate to the platform';
COMMENT ON COLUMN users.employee_id IS 'Optional link to an employee record';
COMMENT ON COLUMN users.failed_login_attempts IS 'Resets on successful login; account locks at 5';

-- ---------------------------------------------------------------------------
-- 3.4  locations
-- ---------------------------------------------------------------------------
CREATE TABLE locations (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    parent_id           UUID        REFERENCES locations(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    type                location_type NOT NULL DEFAULT 'office',
    address             TEXT,
    city                VARCHAR(100),
    state               VARCHAR(100),
    postal_code         VARCHAR(20),
    country             VARCHAR(100),
    latitude            NUMERIC(10,7),
    longitude           NUMERIC(10,7),
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_locations_company_code UNIQUE (company_id, code)
);

COMMENT ON TABLE locations IS 'Physical places — office, warehouse, datacenter, etc.';
COMMENT ON COLUMN locations.parent_id IS 'Self-referencing hierarchy: Building → Floor → Room';

-- ---------------------------------------------------------------------------
-- 3.5  departments
-- ---------------------------------------------------------------------------
CREATE TABLE departments (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    parent_id           UUID        REFERENCES departments(id) ON DELETE SET NULL,
    head_employee_id    UUID,
    location_id         UUID        REFERENCES locations(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    cost_center         VARCHAR(50),
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_departments_company_code UNIQUE (company_id, code)
);

COMMENT ON TABLE departments IS 'Organizational units within a company';
COMMENT ON COLUMN departments.parent_id IS 'Self-referencing for department hierarchy';

-- ---------------------------------------------------------------------------
-- 3.6  employees
-- ---------------------------------------------------------------------------
CREATE TABLE employees (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    department_id       UUID        NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    manager_id          UUID        REFERENCES employees(id) ON DELETE SET NULL,
    location_id         UUID        REFERENCES locations(id) ON DELETE SET NULL,
    employee_code       VARCHAR(50) NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    personal_email      VARCHAR(255),
    phone               VARCHAR(50),
    job_title           VARCHAR(255),
    employment_type     employment_type NOT NULL DEFAULT 'full_time',
    status              employment_status NOT NULL DEFAULT 'active',
    join_date           DATE        NOT NULL,
    resign_date         DATE,
    profile_image_url   VARCHAR(500),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_employees_code_company UNIQUE (company_id, employee_code),
    CONSTRAINT uq_employees_email_company UNIQUE (company_id, email)
);

COMMENT ON TABLE employees IS 'People employed by the company who may hold assets and licenses';
COMMENT ON COLUMN employees.employee_code IS 'HR identifier — immutable after creation';

-- ---------------------------------------------------------------------------
-- 3.7  asset_categories
-- ---------------------------------------------------------------------------
CREATE TABLE asset_categories (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    parent_id           UUID        REFERENCES asset_categories(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    description         TEXT,
    is_depreciable      BOOLEAN     NOT NULL DEFAULT TRUE,
    useful_life_months  INTEGER     CHECK (useful_life_months > 0),
    icon                VARCHAR(50),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_asset_categories_company_code UNIQUE (company_id, code)
);

COMMENT ON TABLE asset_categories IS 'Classification hierarchy for physical assets';

-- ---------------------------------------------------------------------------
-- 3.8  vendors
-- ---------------------------------------------------------------------------
CREATE TABLE vendors (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50)  NOT NULL,
    contact_name        VARCHAR(255),
    contact_email       VARCHAR(255),
    contact_phone       VARCHAR(50),
    website             VARCHAR(255),
    support_phone       VARCHAR(50),
    support_email       VARCHAR(255),
    payment_terms       VARCHAR(100),
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_vendors_company_name UNIQUE (company_id, name)
);

COMMENT ON TABLE vendors IS 'Suppliers of hardware and software';

-- ---------------------------------------------------------------------------
-- 3.9  assets
-- ---------------------------------------------------------------------------
CREATE TABLE assets (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    category_id         UUID        NOT NULL REFERENCES asset_categories(id) ON DELETE RESTRICT,
    location_id         UUID        REFERENCES locations(id) ON DELETE SET NULL,
    vendor_id           UUID        REFERENCES vendors(id) ON DELETE SET NULL,
    asset_tag           VARCHAR(100) NOT NULL,
    serial_number       VARCHAR(255),
    model               VARCHAR(255),
    brand               VARCHAR(255),
    purchase_date       DATE,
    purchase_cost       NUMERIC(12,2) CHECK (purchase_cost >= 0),
    warranty_expiry     DATE,
    status              asset_status NOT NULL DEFAULT 'available',
    condition           asset_condition NOT NULL DEFAULT 'good',
    specifications      JSONB       DEFAULT '{}',
    notes               TEXT,
    last_inventory_date TIMESTAMPTZ,
    assigned_at         TIMESTAMPTZ,
    return_expected_at  TIMESTAMPTZ,
    image_url           VARCHAR(500),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_assets_tag_company UNIQUE (company_id, asset_tag)
);

COMMENT ON TABLE assets IS 'Physical IT assets tracked by the system';
COMMENT ON COLUMN assets.asset_tag IS 'Human-readable tracking number (e.g., AST-00042)';

-- ---------------------------------------------------------------------------
-- 3.10  asset_assignments
-- ---------------------------------------------------------------------------
CREATE TABLE asset_assignments (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    asset_id            UUID        NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    employee_id         UUID        NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    assigned_by         UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    returned_to         UUID        REFERENCES users(id) ON DELETE SET NULL,
    assigned_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expected_return_at  TIMESTAMPTZ,
    returned_at         TIMESTAMPTZ,
    condition_on_assign VARCHAR(50),
    condition_on_return VARCHAR(50),
    notes               TEXT,
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID
);

COMMENT ON TABLE asset_assignments IS 'Tracks which employee currently holds an asset';
COMMENT ON COLUMN asset_assignments.is_active IS 'TRUE for the current assignment; only one active per asset';

-- ---------------------------------------------------------------------------
-- 3.11  asset_histories
-- ---------------------------------------------------------------------------
CREATE TABLE asset_histories (
    id                  BIGSERIAL   PRIMARY KEY,
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    asset_id            UUID        NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    assignment_id       UUID        REFERENCES asset_assignments(id) ON DELETE SET NULL,
    employee_id         UUID        REFERENCES employees(id) ON DELETE SET NULL,
    changed_by          UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type          asset_event_type NOT NULL,
    from_status         asset_status,
    to_status           asset_status,
    from_employee_id    UUID        REFERENCES employees(id) ON DELETE SET NULL,
    to_employee_id      UUID        REFERENCES employees(id) ON DELETE SET NULL,
    from_location_id    UUID        REFERENCES locations(id) ON DELETE SET NULL,
    to_location_id      UUID        REFERENCES locations(id) ON DELETE SET NULL,
    notes               TEXT,
    metadata            JSONB       DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE asset_histories IS 'Immutable audit trail of all asset movements and status changes';
COMMENT ON COLUMN asset_histories.event_type IS 'Type of event that occurred';

-- ---------------------------------------------------------------------------
-- 3.12  softwares
-- ---------------------------------------------------------------------------
CREATE TABLE softwares (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    vendor_id           UUID        REFERENCES vendors(id) ON DELETE SET NULL,
    category_id         UUID        REFERENCES asset_categories(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    publisher           VARCHAR(255),
    version             VARCHAR(100),
    description         TEXT,
    license_model       license_model NOT NULL DEFAULT 'per_seat',
    is_cloud            BOOLEAN     NOT NULL DEFAULT FALSE,
    website             VARCHAR(255),
    support_url         VARCHAR(255),
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_softwares_company_name UNIQUE (company_id, name)
);

COMMENT ON TABLE softwares IS 'Software products that the company licenses';

-- ---------------------------------------------------------------------------
-- 3.13  licenses
-- ---------------------------------------------------------------------------
CREATE TABLE licenses (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    software_id         UUID        NOT NULL REFERENCES softwares(id) ON DELETE CASCADE,
    license_key         VARCHAR(255),
    license_type        license_type NOT NULL DEFAULT 'subscription',
    quantity_purchased  INTEGER     NOT NULL DEFAULT 1 CHECK (quantity_purchased > 0),
    quantity_used       INTEGER     NOT NULL DEFAULT 0 CHECK (quantity_used >= 0),
    unit_price          NUMERIC(12,2) CHECK (unit_price >= 0),
    total_cost          NUMERIC(12,2) CHECK (total_cost >= 0),
    purchase_date       DATE,
    start_date          DATE        NOT NULL,
    expiry_date         DATE,
    renewal_auto        BOOLEAN     NOT NULL DEFAULT FALSE,
    renewal_price       NUMERIC(12,2) CHECK (renewal_price >= 0),
    support_included    BOOLEAN     NOT NULL DEFAULT FALSE,
    notes               TEXT,
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT chk_licenses_quantity_used CHECK (quantity_used <= quantity_purchased)
);

COMMENT ON TABLE licenses IS 'License seats, subscriptions, or entitlements for software products';
COMMENT ON COLUMN licenses.quantity_used IS 'Must never exceed quantity_purchased';
COMMENT ON COLUMN licenses.total_cost IS 'Denormalized: quantity_purchased * unit_price';

-- ---------------------------------------------------------------------------
-- 3.14  employee_softwares (junction: employee ↔ license)
-- ---------------------------------------------------------------------------
CREATE TABLE employee_softwares (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    employee_id         UUID        NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    license_id          UUID        NOT NULL REFERENCES licenses(id) ON DELETE RESTRICT,
    software_id         UUID        NOT NULL REFERENCES softwares(id) ON DELETE RESTRICT,
    assigned_by         UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    revoked_by          UUID        REFERENCES users(id) ON DELETE SET NULL,
    assigned_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at          TIMESTAMPTZ,
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID
);

COMMENT ON TABLE employee_softwares IS 'Junction table linking employees to software license seats';
COMMENT ON COLUMN employee_softwares.software_id IS 'Denormalized for performance — derived from license.software_id';
COMMENT ON COLUMN employee_softwares.is_active IS 'FALSE when access is revoked';

-- ---------------------------------------------------------------------------
-- 3.15  software_usage_logs
-- ---------------------------------------------------------------------------
CREATE TABLE software_usage_logs (
    id                      BIGSERIAL   PRIMARY KEY,
    company_id              UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    employee_software_id    UUID        NOT NULL REFERENCES employee_softwares(id) ON DELETE CASCADE,
    employee_id             UUID        NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    software_id             UUID        NOT NULL REFERENCES softwares(id) ON DELETE CASCADE,
    license_id              UUID        NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    usage_date              DATE        NOT NULL,
    is_active_user          BOOLEAN     NOT NULL DEFAULT FALSE,
    sessions_count          INTEGER     NOT NULL DEFAULT 0 CHECK (sessions_count >= 0),
    total_duration_minutes  INTEGER     CHECK (total_duration_minutes >= 0),
    last_activity_at        TIMESTAMPTZ,
    source                  usage_source NOT NULL DEFAULT 'system',
    metadata                JSONB       DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE software_usage_logs IS 'Daily software usage records — partition by month for scale';
COMMENT ON COLUMN software_usage_logs.is_active_user IS 'TRUE if any activity was detected on this date';

-- ---------------------------------------------------------------------------
-- 3.16  notifications
-- ---------------------------------------------------------------------------
CREATE TABLE notifications (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    message             TEXT        NOT NULL,
    type                notification_type NOT NULL,
    severity            notification_severity NOT NULL DEFAULT 'info',
    reference_type      VARCHAR(50),
    reference_id        UUID,
    is_read             BOOLEAN     NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMPTZ,
    action_url          VARCHAR(500),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE notifications IS 'System-generated alerts for IT managers';
COMMENT ON COLUMN notifications.reference_type IS 'Polymorphic reference: license, asset, etc.';
COMMENT ON COLUMN notifications.reference_id IS 'UUID of the referenced entity';

-- ---------------------------------------------------------------------------
-- 3.17  qr_codes
-- ---------------------------------------------------------------------------
CREATE TABLE qr_codes (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    asset_id            UUID        NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    code                VARCHAR(255) NOT NULL,
    qr_image_url        VARCHAR(500),
    is_printed          BOOLEAN     NOT NULL DEFAULT FALSE,
    printed_at          TIMESTAMPTZ,
    printed_by          UUID        REFERENCES users(id) ON DELETE SET NULL,
    scan_count          INTEGER     NOT NULL DEFAULT 0,
    last_scanned_at     TIMESTAMPTZ,
    last_scanned_by     UUID        REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_qr_codes_code UNIQUE (code),
    CONSTRAINT uq_qr_codes_asset UNIQUE (asset_id)
);

COMMENT ON TABLE qr_codes IS 'Unique QR codes bound one-to-one with physical assets';
COMMENT ON COLUMN qr_codes.code IS 'Globally unique QR value — supports cross-tenant scanning';

-- ---------------------------------------------------------------------------
-- 3.18  ai_chat_histories
-- ---------------------------------------------------------------------------
CREATE TABLE ai_chat_histories (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id          UUID        NOT NULL,
    role                chat_role   NOT NULL,
    content             TEXT        NOT NULL,
    tokens_used         INTEGER     CHECK (tokens_used >= 0),
    model_used          VARCHAR(100),
    retrieved_documents JSONB       DEFAULT '[]',
    feedback_score      INTEGER     CHECK (feedback_score BETWEEN 1 AND 5),
    feedback_text       TEXT,
    latency_ms          INTEGER     CHECK (latency_ms >= 0),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ai_chat_histories IS 'RAG conversation messages — immutable audit of AI interactions';
COMMENT ON COLUMN ai_chat_histories.session_id IS 'Groups messages into a single conversation';
COMMENT ON COLUMN ai_chat_histories.retrieved_documents IS 'Array of document IDs used for RAG context';

-- ---------------------------------------------------------------------------
-- 3.19  ai_predictions
-- ---------------------------------------------------------------------------
CREATE TABLE ai_predictions (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID            NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    prediction_type     prediction_type NOT NULL,
    model_name          VARCHAR(100)    NOT NULL,
    model_version       VARCHAR(50)     NOT NULL,
    target_entity_type  VARCHAR(50),
    target_entity_id    UUID,
    prediction_date     DATE            NOT NULL,
    predicted_value     NUMERIC(14,2)   NOT NULL,
    actual_value        NUMERIC(14,2),
    confidence_score    NUMERIC(5,4)    CHECK (confidence_score BETWEEN 0 AND 1),
    features_used       JSONB           DEFAULT '[]',
    input_snapshot      JSONB,
    is_anomaly          BOOLEAN         NOT NULL DEFAULT FALSE,
    anomaly_score       NUMERIC(5,4)    CHECK (anomaly_score BETWEEN 0 AND 1),
    notes               TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ai_predictions IS 'ML model outputs — forecasts and anomaly detection results';
COMMENT ON COLUMN ai_predictions.actual_value IS 'Populated post-fact by batch job for accuracy tracking';

-- ---------------------------------------------------------------------------
-- 3.20  ai_recommendations
-- ---------------------------------------------------------------------------
CREATE TABLE ai_recommendations (
    id                  UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID                NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    prediction_id       UUID                REFERENCES ai_predictions(id) ON DELETE SET NULL,
    title               VARCHAR(255)        NOT NULL,
    description         TEXT                NOT NULL,
    recommendation_type recommendation_type NOT NULL,
    priority            VARCHAR(20)         NOT NULL DEFAULT 'medium'
                        CHECK (priority IN ('low','medium','high','critical')),
    estimated_savings   NUMERIC(12,2)       CHECK (estimated_savings >= 0),
    action_entity_type  VARCHAR(50),
    action_entity_id    UUID,
    action_url          VARCHAR(500),
    status              recommendation_status NOT NULL DEFAULT 'pending',
    applied_at          TIMESTAMPTZ,
    applied_by          UUID                REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID
);

COMMENT ON TABLE ai_recommendations IS 'Actionable business recommendations derived from AI predictions';

-- ---------------------------------------------------------------------------
-- 3.21  audit_logs
-- ---------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id                  BIGSERIAL   PRIMARY KEY,
    company_id          UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id             UUID        REFERENCES users(id) ON DELETE SET NULL,
    action              VARCHAR(100) NOT NULL,
    entity_type         VARCHAR(100) NOT NULL,
    entity_id           UUID        NOT NULL,
    previous_values     JSONB,
    new_values          JSONB,
    ip_address          VARCHAR(45),
    user_agent          TEXT,
    session_id          VARCHAR(255),
    correlation_id      UUID,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Immutable security and compliance audit trail — append-only';

-- ---------------------------------------------------------------------------
-- 3.22  system_settings
-- ---------------------------------------------------------------------------
CREATE TABLE system_settings (
    id                  UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID                REFERENCES companies(id) ON DELETE CASCADE,
    key                 VARCHAR(255)        NOT NULL,
    value               TEXT                NOT NULL,
    value_type          setting_value_type  NOT NULL DEFAULT 'string',
    description         TEXT,
    is_encrypted        BOOLEAN             NOT NULL DEFAULT FALSE,
    is_editable         BOOLEAN             NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    created_by          UUID,
    updated_by          UUID,
    CONSTRAINT uq_settings_company_key UNIQUE (company_id, key)
);

COMMENT ON TABLE system_settings IS 'Key-value configuration store — global (company_id NULL) or per-company';
COMMENT ON COLUMN system_settings.company_id IS 'NULL for global settings that apply to all companies';

-- ############################################################################
-- 4. FOREIGN KEY CONSTRAINTS (deferred cross-references)
-- ############################################################################

-- Department head_employee_id references employees (must exist after employees)
ALTER TABLE departments
    ADD CONSTRAINT fk_departments_head_employee
    FOREIGN KEY (head_employee_id) REFERENCES employees(id) ON DELETE SET NULL;

-- Employee manager_id references employees (self-referencing)
-- Already defined inline, but add explicit FK name
ALTER TABLE employees
    ADD CONSTRAINT fk_employees_manager
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL;

-- User employee_id references employees (1:1)
ALTER TABLE users
    ADD CONSTRAINT fk_users_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL;

-- ############################################################################
-- 5. INDEXES
-- ############################################################################

-- 5.1  companies
CREATE INDEX idx_companies_is_active ON companies(is_active) WHERE deleted_at IS NULL;

-- 5.2  roles
CREATE INDEX idx_roles_company ON roles(company_id);

-- 5.3  users
CREATE INDEX idx_users_email ON users(company_id, email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_employee ON users(employee_id) WHERE employee_id IS NOT NULL;
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_last_login ON users(last_login_at) WHERE last_login_at IS NOT NULL;

-- 5.4  locations
CREATE INDEX idx_locations_company_type ON locations(company_id, type);
CREATE INDEX idx_locations_parent ON locations(parent_id);

-- 5.5  departments
CREATE INDEX idx_departments_company_parent ON departments(company_id, parent_id);
CREATE INDEX idx_departments_head ON departments(head_employee_id);

-- 5.6  employees
CREATE INDEX idx_employees_company_dept ON employees(company_id, department_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_employees_status ON employees(company_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employees_email ON employees(company_id, email) WHERE deleted_at IS NULL;
CREATE INDEX idx_employees_code ON employees(company_id, employee_code) WHERE deleted_at IS NULL;

-- 5.7  asset_categories
CREATE INDEX idx_asset_categories_company ON asset_categories(company_id);
CREATE INDEX idx_asset_categories_tree ON asset_categories(company_id, parent_id);

-- 5.8  vendors
CREATE INDEX idx_vendors_company ON vendors(company_id);

-- 5.9  assets
CREATE INDEX idx_assets_company_status ON assets(company_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_serial ON assets(serial_number);
CREATE INDEX idx_assets_category ON assets(category_id);
CREATE INDEX idx_assets_vendor ON assets(vendor_id);
CREATE INDEX idx_assets_assigned_at ON assets(company_id, assigned_at) WHERE assigned_at IS NOT NULL;

-- 5.10  asset_assignments
CREATE INDEX idx_assignments_employee_active
    ON asset_assignments(employee_id) WHERE is_active = TRUE;
CREATE INDEX idx_assignments_expected_return
    ON asset_assignments(expected_return_at) WHERE returned_at IS NULL;

-- Partial unique index: one active assignment per asset
CREATE UNIQUE INDEX uq_assignments_active_asset
    ON asset_assignments(asset_id) WHERE is_active = TRUE;

-- 5.11  asset_histories
CREATE INDEX idx_asset_histories_asset_time ON asset_histories(asset_id, created_at);
CREATE INDEX idx_asset_histories_company_date ON asset_histories(company_id, created_at);
CREATE INDEX idx_asset_histories_event_type ON asset_histories(company_id, event_type);
CREATE INDEX idx_asset_histories_employee ON asset_histories(employee_id);

-- 5.12  softwares
CREATE INDEX idx_softwares_company_active ON softwares(company_id, is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_softwares_vendor ON softwares(vendor_id);

-- 5.13  licenses
CREATE INDEX idx_licenses_software_active ON licenses(software_id, is_active);
CREATE INDEX idx_licenses_expiry ON licenses(company_id, expiry_date) WHERE is_active = TRUE;
CREATE INDEX idx_licenses_utilization ON licenses(software_id, quantity_purchased, quantity_used);

-- 5.14  employee_softwares
CREATE INDEX idx_emp_softwares_active_emp
    ON employee_softwares(employee_id) WHERE is_active = TRUE;
CREATE INDEX idx_emp_softwares_active_license
    ON employee_softwares(license_id) WHERE is_active = TRUE;
CREATE INDEX idx_emp_softwares_software
    ON employee_softwares(software_id, company_id);

-- Partial unique index: one active assignment per employee-license pair
CREATE UNIQUE INDEX uq_emp_softwares_active
    ON employee_softwares(employee_id, license_id) WHERE is_active = TRUE;

-- 5.15  software_usage_logs
CREATE INDEX idx_usage_logs_company_date ON software_usage_logs(company_id, usage_date);
CREATE INDEX idx_usage_logs_software_date ON software_usage_logs(software_id, usage_date);
CREATE INDEX idx_usage_logs_emp_software ON software_usage_logs(employee_software_id, usage_date);

-- Composite index for dormant account detection
CREATE INDEX idx_usage_logs_dormant
    ON software_usage_logs(license_id, usage_date, is_active_user);

-- Monthly aggregation index for forecasting
CREATE INDEX idx_usage_logs_monthly
    ON softwares(company_id) WHERE deleted_at IS NULL;

-- 5.16  notifications
CREATE INDEX idx_notifications_user_unread
    ON notifications(user_id) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_company_type ON notifications(company_id, type);
CREATE INDEX idx_notifications_created ON notifications(user_id, created_at);

-- 5.17  qr_codes
-- Unique indexes are declared inline (uq_qr_codes_code, uq_qr_codes_asset)
CREATE INDEX idx_qr_codes_company ON qr_codes(company_id);

-- 5.18  ai_chat_histories
CREATE INDEX idx_chat_sessions ON ai_chat_histories(company_id, session_id, created_at);
CREATE INDEX idx_chat_user ON ai_chat_histories(company_id, user_id, created_at);
CREATE INDEX idx_chat_feedback ON ai_chat_histories(feedback_score)
    WHERE feedback_score IS NOT NULL;
CREATE INDEX idx_chat_created ON ai_chat_histories(created_at);

-- 5.19  ai_predictions
CREATE INDEX idx_predictions_type_date
    ON ai_predictions(company_id, prediction_type, prediction_date);
CREATE INDEX idx_predictions_entity
    ON ai_predictions(target_entity_id, prediction_type);
CREATE INDEX idx_predictions_accuracy
    ON ai_predictions(model_name, actual_value) WHERE actual_value IS NOT NULL;

-- 5.20  ai_recommendations
CREATE INDEX idx_recommendations_company_status
    ON ai_recommendations(company_id, status);
CREATE INDEX idx_recommendations_type_priority
    ON ai_recommendations(recommendation_type, priority);
CREATE INDEX idx_recommendations_prediction
    ON ai_recommendations(prediction_id);

-- 5.21  audit_logs
CREATE INDEX idx_audit_logs_entity
    ON audit_logs(entity_type, entity_id, created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_logs_action_time ON audit_logs(company_id, action, created_at);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- 5.22  system_settings
CREATE INDEX idx_settings_lookup ON system_settings(company_id, key);

-- ############################################################################
-- 6. TRIGGERS
-- ############################################################################

-- ---------------------------------------------------------------------------
-- 6.1  Automatic updated_at trigger function
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with an updated_at column
CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_departments_updated_at
    BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_locations_updated_at
    BEFORE UPDATE ON locations FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_asset_categories_updated_at
    BEFORE UPDATE ON asset_categories FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_vendors_updated_at
    BEFORE UPDATE ON vendors FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_assets_updated_at
    BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_asset_assignments_updated_at
    BEFORE UPDATE ON asset_assignments FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_softwares_updated_at
    BEFORE UPDATE ON softwares FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_licenses_updated_at
    BEFORE UPDATE ON licenses FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_employee_softwares_updated_at
    BEFORE UPDATE ON employee_softwares FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_qr_codes_updated_at
    BEFORE UPDATE ON qr_codes FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_ai_recommendations_updated_at
    BEFORE UPDATE ON ai_recommendations FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER trg_system_settings_updated_at
    BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- ---------------------------------------------------------------------------
-- 6.2  Asset assignment: auto-create asset_history on insert
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_asset_assignment_history()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO asset_histories (
        company_id,
        asset_id,
        assignment_id,
        employee_id,
        changed_by,
        event_type,
        from_status,
        to_status,
        from_employee_id,
        to_employee_id,
        from_location_id,
        to_location_id,
        notes,
        created_at
    ) VALUES (
        NEW.company_id,
        NEW.asset_id,
        NEW.id,
        NEW.employee_id,
        NEW.assigned_by,
        'assigned',
        'available',
        'assigned',
        NULL,
        NEW.employee_id,
        NULL,
        (SELECT location_id FROM assets WHERE id = NEW.asset_id),
        NEW.notes,
        NOW()
    );

    -- Update the asset status and assignment timestamp
    UPDATE assets
    SET status = 'assigned',
        assigned_at = NEW.assigned_at,
        updated_at = NOW()
    WHERE id = NEW.asset_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_asset_assignment_after_insert
    AFTER INSERT ON asset_assignments FOR EACH ROW
    WHEN (NEW.is_active = TRUE)
    EXECUTE FUNCTION trigger_asset_assignment_history();

-- ---------------------------------------------------------------------------
-- 6.3  Asset return: auto-create asset_history and update asset status
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_asset_return_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.returned_at IS NOT NULL AND OLD.returned_at IS NULL THEN
        INSERT INTO asset_histories (
            company_id,
            asset_id,
            assignment_id,
            employee_id,
            changed_by,
            event_type,
            from_status,
            to_status,
            from_employee_id,
            to_employee_id,
            notes,
            created_at
        ) VALUES (
            NEW.company_id,
            NEW.asset_id,
            NEW.id,
            NEW.employee_id,
            COALESCE(NEW.returned_to, NEW.assigned_by),
            'returned',
            'assigned',
            'available',
            NEW.employee_id,
            NULL,
            NEW.notes,
            NOW()
        );

        -- Update asset status back to available
        UPDATE assets
        SET status = 'available',
            assigned_at = NULL,
            updated_at = NOW()
        WHERE id = NEW.asset_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_asset_assignment_after_return
    AFTER UPDATE ON asset_assignments FOR EACH ROW
    EXECUTE FUNCTION trigger_asset_return_history();

-- ---------------------------------------------------------------------------
-- 6.4  Denormalize total_cost on license insert/update
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_license_calc_total()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.unit_price IS NOT NULL AND NEW.quantity_purchased IS NOT NULL THEN
        NEW.total_cost = NEW.unit_price * NEW.quantity_purchased;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_license_calc_total
    BEFORE INSERT OR UPDATE ON licenses FOR EACH ROW
    EXECUTE FUNCTION trigger_license_calc_total();

-- ---------------------------------------------------------------------------
-- 6.5  Prevent hard delete on append-only tables
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_prevent_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Rows in % cannot be deleted — table is append-only', TG_TABLE_NAME
        USING HINT = 'Use soft delete or archival process instead';
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_asset_histories_no_delete
    BEFORE DELETE ON asset_histories FOR EACH ROW
    EXECUTE FUNCTION trigger_prevent_delete();

CREATE TRIGGER trg_audit_logs_no_delete
    BEFORE DELETE ON audit_logs FOR EACH ROW
    EXECUTE FUNCTION trigger_prevent_delete();

CREATE TRIGGER trg_ai_chat_histories_no_delete
    BEFORE DELETE ON ai_chat_histories FOR EACH ROW
    EXECUTE FUNCTION trigger_prevent_delete();

-- ############################################################################
-- 7. VIEWS
-- ############################################################################

-- ---------------------------------------------------------------------------
-- 7.1  vw_asset_summary — aggregate view per company
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_asset_summary AS
SELECT
    a.company_id,
    c.name AS company_name,
    ac.name AS category_name,
    a.status,
    COUNT(*) AS asset_count,
    COUNT(*) FILTER (WHERE a.condition IN ('new','good')) AS healthy_count,
    COUNT(*) FILTER (WHERE a.condition IN ('poor','damaged','repairing')) AS damaged_count,
    COALESCE(SUM(a.purchase_cost), 0) AS total_value
FROM assets a
JOIN companies c ON c.id = a.company_id
JOIN asset_categories ac ON ac.id = a.category_id
WHERE a.deleted_at IS NULL
GROUP BY a.company_id, c.name, ac.name, a.status;

COMMENT ON VIEW vw_asset_summary IS 'Asset counts and value grouped by company, category, and status';

-- ---------------------------------------------------------------------------
-- 7.2  vw_license_usage — utilization per software
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_license_usage AS
SELECT
    l.company_id,
    c.name AS company_name,
    sw.name AS software_name,
    sw.license_model,
    COUNT(DISTINCT l.id) AS total_licenses,
    COALESCE(SUM(l.quantity_purchased), 0) AS total_seats_purchased,
    COALESCE(SUM(l.quantity_used), 0) AS total_seats_used,
    CASE
        WHEN COALESCE(SUM(l.quantity_purchased), 0) > 0
        THEN ROUND(
            (COALESCE(SUM(l.quantity_used), 0)::NUMERIC / SUM(l.quantity_purchased)) * 100,
            2
        )
        ELSE 0
    END AS utilization_pct,
    COUNT(DISTINCT l.id) FILTER (WHERE l.expiry_date <= NOW() + INTERVAL '30 days' AND l.expiry_date IS NOT NULL) AS expiring_soon_count
FROM licenses l
JOIN companies c ON c.id = l.company_id
JOIN softwares sw ON sw.id = l.software_id
WHERE l.deleted_at IS NULL AND l.is_active = TRUE
GROUP BY l.company_id, c.name, sw.name, sw.license_model;

COMMENT ON VIEW vw_license_usage IS 'License utilization metrics per software product';

-- ---------------------------------------------------------------------------
-- 7.3  vw_department_assets — assets assigned per department
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_department_assets AS
SELECT
    d.company_id,
    d.id AS department_id,
    d.name AS department_name,
    d.code AS department_code,
    ac.name AS category_name,
    COUNT(DISTINCT a.id) AS total_assets,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'assigned') AS assigned_assets,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'maintenance') AS maintenance_assets,
    COUNT(DISTINCT emp.id) AS employee_count,
    COUNT(DISTINCT aa.id) FILTER (WHERE aa.is_active = TRUE) AS active_assignments
FROM departments d
LEFT JOIN employees emp ON emp.department_id = d.id AND emp.deleted_at IS NULL
LEFT JOIN asset_assignments aa ON aa.employee_id = emp.id AND aa.is_active = TRUE
LEFT JOIN assets a ON a.id = aa.asset_id AND a.deleted_at IS NULL
LEFT JOIN asset_categories ac ON ac.id = a.category_id
WHERE d.deleted_at IS NULL
GROUP BY d.company_id, d.id, d.name, d.code, ac.name;

COMMENT ON VIEW vw_department_assets IS 'Asset distribution across departments';

-- ---------------------------------------------------------------------------
-- 7.4  vw_employee_assets — what each employee currently holds
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_employee_assets AS
SELECT
    emp.company_id,
    emp.id AS employee_id,
    emp.first_name || ' ' || emp.last_name AS employee_name,
    emp.employee_code,
    emp.email,
    d.name AS department_name,
    a.id AS asset_id,
    a.asset_tag,
    a.brand,
    a.model,
    a.serial_number,
    ac.name AS category_name,
    aa.assigned_at,
    aa.expected_return_at,
    a.status AS asset_status,
    a.condition AS asset_condition
FROM employees emp
JOIN departments d ON d.id = emp.department_id
JOIN asset_assignments aa ON aa.employee_id = emp.id AND aa.is_active = TRUE
JOIN assets a ON a.id = aa.asset_id AND a.deleted_at IS NULL
JOIN asset_categories ac ON ac.id = a.category_id
WHERE emp.deleted_at IS NULL;

COMMENT ON VIEW vw_employee_assets IS 'Current asset holdings per employee';

-- ---------------------------------------------------------------------------
-- 7.5  vw_employee_software — current software assignments per employee
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_employee_software AS
SELECT
    emp.company_id,
    emp.id AS employee_id,
    emp.first_name || ' ' || emp.last_name AS employee_name,
    emp.employee_code,
    d.name AS department_name,
    sw.id AS software_id,
    sw.name AS software_name,
    sw.license_model,
    l.id AS license_id,
    l.license_type,
    l.expiry_date,
    es.assigned_at,
    es.is_active
FROM employees emp
JOIN departments d ON d.id = emp.department_id
JOIN employee_softwares es ON es.employee_id = emp.id AND es.is_active = TRUE
JOIN softwares sw ON sw.id = es.software_id
JOIN licenses l ON l.id = es.license_id
WHERE emp.deleted_at IS NULL;

COMMENT ON VIEW vw_employee_software IS 'Current software license assignments per employee';

-- ---------------------------------------------------------------------------
-- 7.6  vw_ai_predictions — latest predictions with recommendations
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ai_predictions AS
SELECT
    p.id AS prediction_id,
    p.company_id,
    p.prediction_type,
    p.model_name,
    p.model_version,
    p.prediction_date,
    p.predicted_value,
    p.actual_value,
    p.confidence_score,
    p.is_anomaly,
    p.anomaly_score,
    r.id AS recommendation_id,
    r.title AS recommendation_title,
    r.recommendation_type,
    r.priority,
    r.estimated_savings,
    r.status AS recommendation_status,
    p.created_at
FROM ai_predictions p
LEFT JOIN ai_recommendations r ON r.prediction_id = p.id;

COMMENT ON VIEW vw_ai_predictions IS 'AI predictions joined with their recommendations';

-- ---------------------------------------------------------------------------
-- 7.7  vw_dashboard_metrics — ready-to-query dashboard KPIs
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_dashboard_metrics AS
SELECT
    c.id AS company_id,
    c.name AS company_name,
    (SELECT COUNT(*) FROM employees e WHERE e.company_id = c.id AND e.deleted_at IS NULL AND e.status IN ('active','notice')) AS active_employees,
    (SELECT COUNT(*) FROM assets a WHERE a.company_id = c.id AND a.deleted_at IS NULL) AS total_assets,
    (SELECT COUNT(*) FROM assets a WHERE a.company_id = c.id AND a.deleted_at IS NULL AND a.status = 'assigned') AS assigned_assets,
    (SELECT COUNT(*) FROM assets a WHERE a.company_id = c.id AND a.deleted_at IS NULL AND a.status = 'available') AS available_assets,
    (SELECT COUNT(*) FROM assets a WHERE a.company_id = c.id AND a.deleted_at IS NULL AND a.status IN ('lost','stolen')) AS lost_assets,
    (SELECT COUNT(*) FROM asset_assignments aa WHERE aa.company_id = c.id AND aa.is_active = TRUE) AS active_assignments,
    (SELECT COALESCE(SUM(l.quantity_purchased), 0) FROM licenses l WHERE l.company_id = c.id AND l.deleted_at IS NULL) AS total_license_seats,
    (SELECT COALESCE(SUM(l.quantity_used), 0) FROM licenses l WHERE l.company_id = c.id AND l.deleted_at IS NULL) AS used_license_seats,
    (SELECT COUNT(*) FROM licenses l WHERE l.company_id = c.id AND l.deleted_at IS NULL AND l.is_active = TRUE AND l.expiry_date <= NOW() + INTERVAL '30 days' AND l.expiry_date IS NOT NULL) AS licenses_expiring_30d,
    (SELECT COUNT(*) FROM notifications n WHERE n.company_id = c.id AND n.is_read = FALSE) AS unread_notifications,
    (SELECT COALESCE(SUM(r.estimated_savings), 0) FROM ai_recommendations r WHERE r.company_id = c.id AND r.status = 'applied') AS realized_savings
FROM companies c
WHERE c.deleted_at IS NULL;

COMMENT ON VIEW vw_dashboard_metrics IS 'Pre-aggregated dashboard KPIs per company';

-- ############################################################################
-- 8. ROW-LEVEL SECURITY (RLS)
-- ################################################################------------

-- Enable RLS on all tenant-scoped tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_histories ENABLE ROW LEVEL SECURITY;
ALTER TABLE softwares ENABLE ROW LEVEL SECURITY;
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_softwares ENABLE ROW LEVEL SECURITY;
ALTER TABLE software_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_histories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Create a default tenant isolation policy for each table
-- A session variable 'app.current_company_id' must be set by the backend
-- after authentication.

CREATE POLICY p_companies_tenant ON companies
    USING (id = current_setting('app.current_company_id')::UUID OR current_setting('app.is_super_admin') = 'true');

CREATE POLICY p_roles_tenant ON roles
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_users_tenant ON users
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_departments_tenant ON departments
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_employees_tenant ON employees
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_locations_tenant ON locations
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_asset_categories_tenant ON asset_categories
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_vendors_tenant ON vendors
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_assets_tenant ON assets
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_asset_assignments_tenant ON asset_assignments
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_asset_histories_tenant ON asset_histories
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_softwares_tenant ON softwares
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_licenses_tenant ON licenses
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_employee_softwares_tenant ON employee_softwares
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_software_usage_logs_tenant ON software_usage_logs
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_notifications_tenant ON notifications
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_qr_codes_tenant ON qr_codes
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_ai_chat_histories_tenant ON ai_chat_histories
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_ai_predictions_tenant ON ai_predictions
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_ai_recommendations_tenant ON ai_recommendations
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_audit_logs_tenant ON audit_logs
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY p_system_settings_tenant ON system_settings
    USING (company_id = current_setting('app.current_company_id')::UUID OR company_id IS NULL);

-- ############################################################################
-- 9. END OF SCHEMA
-- ############################################################################
