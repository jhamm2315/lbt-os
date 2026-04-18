-- Run this in Supabase SQL Editor
-- Switches from Clerk Organizations to simple user-based tenancy

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS clerk_user_id TEXT;
CREATE INDEX IF NOT EXISTS idx_orgs_clerk_user_id ON organizations(clerk_user_id);

-- If you had any existing rows, you can delete them cleanly:
-- TRUNCATE organizations CASCADE;
