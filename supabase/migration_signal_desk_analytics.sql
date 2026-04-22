-- Signal Desk analytics artifacts
-- Run after migration_messages.sql.

ALTER TABLE messages
    ADD COLUMN IF NOT EXISTS analytics JSONB;

CREATE INDEX IF NOT EXISTS idx_messages_analytics
    ON messages USING GIN (analytics)
    WHERE analytics IS NOT NULL;
