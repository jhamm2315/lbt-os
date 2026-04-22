-- Signal Desk room membership + notifications
-- Run after migration_messages.sql.

CREATE TABLE IF NOT EXISTS message_channel_members (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    channel_id  UUID NOT NULL REFERENCES message_channels(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'member',
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(channel_id, user_id)
);

CREATE TABLE IF NOT EXISTS message_notifications (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    channel_id  UUID NOT NULL REFERENCES message_channels(id) ON DELETE CASCADE,
    message_id  UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'unread',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at     TIMESTAMPTZ,
    UNIQUE(message_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_mcm_channel ON message_channel_members(channel_id);
CREATE INDEX IF NOT EXISTS idx_mcm_user ON message_channel_members(org_id, user_id);
CREATE INDEX IF NOT EXISTS idx_msg_notif_user ON message_notifications(org_id, user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_msg_notif_channel ON message_notifications(channel_id, created_at DESC);

ALTER TABLE message_channel_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "message_channel_members_all" ON message_channel_members
    FOR ALL USING (org_id = auth_org_id()) WITH CHECK (org_id = auth_org_id());

CREATE POLICY "message_notifications_all" ON message_notifications
    FOR ALL USING (org_id = auth_org_id()) WITH CHECK (org_id = auth_org_id());
