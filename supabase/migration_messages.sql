-- =============================================================
-- LBT OS — Messaging System
-- Run in Supabase SQL Editor after the base schema.
-- =============================================================

-- ----------------------------------------------------------
-- CHANNELS
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS message_channels (
    id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name         TEXT        NOT NULL,
    channel_type TEXT        NOT NULL DEFAULT 'team',  -- team | ai_assistant | announcements
    description  TEXT,
    created_by   TEXT,       -- clerk_user_id
    is_archived  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, name)
);

-- ----------------------------------------------------------
-- MESSAGES
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    channel_id   UUID        NOT NULL REFERENCES message_channels(id) ON DELETE CASCADE,
    sender_id    TEXT        NOT NULL,   -- clerk_user_id or 'ai_assistant'
    sender_name  TEXT        NOT NULL,
    content      TEXT        NOT NULL DEFAULT '',
    message_type TEXT        NOT NULL DEFAULT 'text',  -- text | gif | ai_response | system
    gif_url      TEXT,
    reply_to_id  UUID        REFERENCES messages(id) ON DELETE SET NULL,
    reactions    JSONB       NOT NULL DEFAULT '{}',    -- {"👍": ["user_id_1", ...]}
    is_edited    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------
-- FILE ATTACHMENTS
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS message_files (
    id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    channel_id   UUID        NOT NULL REFERENCES message_channels(id) ON DELETE CASCADE,
    message_id   UUID        REFERENCES messages(id) ON DELETE SET NULL,
    uploader_id  TEXT        NOT NULL,   -- clerk_user_id
    filename     TEXT        NOT NULL,
    file_type    TEXT        NOT NULL,   -- pdf | docx | xlsx | pptx | csv | image | video | other
    content_type TEXT        NOT NULL,
    file_size    INTEGER     NOT NULL,
    storage_path TEXT        NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------
-- INDEXES
-- ----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_message_channels_org    ON message_channels(org_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel        ON messages(channel_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_org            ON messages(org_id);
CREATE INDEX IF NOT EXISTS idx_message_files_message   ON message_files(message_id);
CREATE INDEX IF NOT EXISTS idx_message_files_channel   ON message_files(channel_id);

-- ----------------------------------------------------------
-- UPDATED_AT TRIGGERS
-- ----------------------------------------------------------
DROP TRIGGER IF EXISTS trg_message_channels_updated ON message_channels;
CREATE TRIGGER trg_message_channels_updated
    BEFORE UPDATE ON message_channels
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

DROP TRIGGER IF EXISTS trg_messages_updated ON messages;
CREATE TRIGGER trg_messages_updated
    BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- ----------------------------------------------------------
-- RLS (service key bypasses these; anon key users need them)
-- ----------------------------------------------------------
ALTER TABLE message_channels  ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages           ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_files      ENABLE ROW LEVEL SECURITY;

CREATE POLICY "message_channels_all" ON message_channels
    FOR ALL USING (org_id = auth_org_id()) WITH CHECK (org_id = auth_org_id());

CREATE POLICY "messages_all" ON messages
    FOR ALL USING (org_id = auth_org_id()) WITH CHECK (org_id = auth_org_id());

CREATE POLICY "message_files_all" ON message_files
    FOR ALL USING (org_id = auth_org_id()) WITH CHECK (org_id = auth_org_id());
