PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. IDENTITÉ & CONFIGURATION DU TENANT
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'deactivating', 'deactivated')),
    api_key_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS tenant_configs (
    tenant_id TEXT PRIMARY KEY,
    qualification_threshold INTEGER NOT NULL DEFAULT 70
        CHECK (qualification_threshold BETWEEN 0 AND 100),
    score_half_life_days INTEGER NOT NULL DEFAULT 30
        CHECK (score_half_life_days > 0),
    campaign_cooldown_days INTEGER NOT NULL DEFAULT 7
        CHECK (campaign_cooldown_days >= 0),
    marketing_global_cooldown_hours INTEGER NOT NULL DEFAULT 48
        CHECK (marketing_global_cooldown_hours >= 0),
    max_emails_weekly INTEGER NOT NULL DEFAULT 2
        CHECK (max_emails_weekly > 0),
    daily_quota INTEGER NOT NULL DEFAULT 500
        CHECK (daily_quota > 0),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- ============================================================================
-- 2. GESTION DES PROSPECTS & HISTORIQUE D'ACTIVITÉ
-- ============================================================================
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    nom TEXT NOT NULL,
    email TEXT NOT NULL,
    score_raw NUMERIC(5,2) NOT NULL DEFAULT 0.00
        CHECK (score_raw BETWEEN 0.00 AND 100.00),
    status TEXT NOT NULL DEFAULT 'NEW'
        CHECK (status IN ('NEW', 'ENGAGED', 'NURTURING', 'QUALIFIED', 'CONVERTED', 'UNSUBSCRIBED')),
    last_activity_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, email),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    prospect_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    points NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    idempotency_key TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, idempotency_key),
    FOREIGN KEY (tenant_id, prospect_id) REFERENCES prospects(tenant_id, id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. COMMANDES & HISTORIQUE DES ÉVÉNEMENTS DE COMMANDE (IDEMPOTENT)
-- ============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    numero_commande TEXT NOT NULL,
    client_email TEXT NOT NULL,
    status TEXT NOT NULL,
    montant_total_ht NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    payload TEXT NOT NULL,
    received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, numero_commande),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    order_id INTEGER NOT NULL,
    numero_commande TEXT NOT NULL,
    status TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, idempotency_key),
    FOREIGN KEY (tenant_id, order_id) REFERENCES orders(tenant_id, id) ON DELETE CASCADE
);

-- ============================================================================
-- 4. MODÈLES D'EMAILS, CAMPAGNES & DISPATCHES
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    html_body TEXT NOT NULL,
    text_body TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, name),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'marketing'
        CHECK (category IN ('marketing', 'transactional')),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused')),
    template_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    -- Suppression du template : restreinte pour forcer la réaffectation explicite
    FOREIGN KEY (tenant_id, template_id) REFERENCES email_templates(tenant_id, id) ON DELETE RESTRICT
);

-- Déclenchements logiques (Dispatches)
CREATE TABLE IF NOT EXISTS campaign_dispatches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    campaign_id INTEGER NOT NULL,
    prospect_id INTEGER NOT NULL,
    category TEXT NOT NULL DEFAULT 'marketing'
        CHECK (category IN ('marketing', 'transactional')),
    idempotency_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SENT', 'FAILED', 'SKIPPED')),
    skip_reason TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, idempotency_key),
    FOREIGN KEY (tenant_id, campaign_id) REFERENCES campaigns(tenant_id, id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id, prospect_id) REFERENCES prospects(tenant_id, id) ON DELETE CASCADE
);

-- Journal d'exécution technique rattaché uniquement au dispatch
CREATE TABLE IF NOT EXISTS campaign_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    dispatch_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    message_id TEXT,
    error_message TEXT,
    sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (tenant_id, dispatch_id) REFERENCES campaign_dispatches(tenant_id, id) ON DELETE CASCADE
);

-- ============================================================================
-- 5. TRANSACTIONAL OUTBOX AVEC VERROUILLAGE SÉCURISÉ
-- ============================================================================
CREATE TABLE IF NOT EXISTS outbox_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'PUBLISHED', 'FAILED')),
    attempts INTEGER NOT NULL DEFAULT 0,
    locked_by TEXT,
    locked_until TEXT,
    next_retry_at TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    published_at TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- ============================================================================
-- 6. EXCLUSIONS & DÉSINCRIPTIONS (RGPD)
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_suppressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    email TEXT NOT NULL,
    reason TEXT NOT NULL
        CHECK (reason IN ('opt_out', 'hard_bounce', 'complaint', 'manual')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (tenant_id, email),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- ============================================================================
-- 7. SÉCURITÉ DU DASHBOARD (ADMINISTRATION SÉPARÉE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'tenant_admin'
        CHECK (role IN ('superadmin', 'tenant_admin')),
    tenant_id TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_sessions (
    id TEXT PRIMARY KEY,
    token_hash TEXT UNIQUE NOT NULL,
    csrf_token_hash TEXT NOT NULL,
    admin_user_id INTEGER NOT NULL,
    tenant_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    revoked INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (admin_user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- ============================================================================
-- 8. AUDIT ANONYME DE PURGE (ZÉRO PII - HASH IRRÉVERSIBLE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenant_purge_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_hash TEXT NOT NULL, -- SHA-256 du tenant_id avec sel serveur (non réversible)
    purged_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    records_deleted INTEGER NOT NULL,
    status TEXT NOT NULL,
    executed_by TEXT NOT NULL
);

-- ============================================================================
-- 9. INDEX DE RECHERCHE ET DE PERFORMANCE MULTI-TENANT
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_prospects_lookup ON prospects(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_activities_timeline ON activities(tenant_id, prospect_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_orders_lookup ON orders(tenant_id, numero_commande);
CREATE INDEX IF NOT EXISTS idx_order_events_history ON order_events(tenant_id, order_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_order_events_idempotency ON order_events(tenant_id, idempotency_key);
CREATE INDEX IF NOT EXISTS idx_dispatches_cooldown ON campaign_dispatches(tenant_id, prospect_id, campaign_id, created_at);
CREATE INDEX IF NOT EXISTS idx_dispatches_category ON campaign_dispatches(tenant_id, prospect_id, category, created_at);
CREATE INDEX IF NOT EXISTS idx_outbox_queue ON outbox_events(status, locked_until, next_retry_at);
CREATE INDEX IF NOT EXISTS idx_suppressions_check ON email_suppressions(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_token ON admin_sessions(token_hash, revoked, expires_at);
