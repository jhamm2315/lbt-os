-- =============================================================
-- Stripe webhook idempotency table
-- Stores processed Stripe event IDs to prevent duplicate processing
-- on Stripe retries.  Run once against your Supabase project.
-- =============================================================

CREATE TABLE IF NOT EXISTS stripe_events (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    stripe_event_id TEXT        UNIQUE NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast duplicate check
CREATE INDEX IF NOT EXISTS idx_stripe_events_event_id ON stripe_events (stripe_event_id);
