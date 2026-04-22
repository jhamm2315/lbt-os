-- Visitor and onboarding event capture.
-- Stores anonymous landing activity and high-signal onboarding submissions for admin review.

CREATE TABLE IF NOT EXISTS visitor_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL CHECK (event_type IN ('page_view', 'cta_click', 'info_submitted', 'test_ping')),
    visitor_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    clerk_user_id TEXT,
    path TEXT NOT NULL DEFAULT '/',
    source TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    referrer TEXT,
    user_agent TEXT,
    ip_hash TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_visitor_events_occurred_at
    ON visitor_events (occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_visitor_events_type_time
    ON visitor_events (event_type, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_visitor_events_visitor
    ON visitor_events (visitor_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_visitor_events_metadata
    ON visitor_events USING GIN (metadata);

