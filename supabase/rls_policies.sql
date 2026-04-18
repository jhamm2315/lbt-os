-- =============================================================
-- LBT OS — Row Level Security Policies
--
-- Design note: The FastAPI backend uses the Supabase SERVICE ROLE
-- key, which bypasses RLS. These policies exist as a defense-in-depth
-- layer for future direct-client access (e.g., mobile apps using
-- Supabase's anon key + custom JWTs with org_id claims).
--
-- If you add a mobile app or edge function that uses the anon key,
-- set a custom JWT claim: { "org_id": "<uuid>" }
-- =============================================================

ALTER TABLE organizations  ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads           ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers       ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales           ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses        ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_reports   ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_sync_runs   ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_record_links ENABLE ROW LEVEL SECURITY;

-- Helper: extract org_id from custom JWT claim
-- Requires JWT payload: { "org_id": "<uuid>" }
CREATE OR REPLACE FUNCTION auth_org_id() RETURNS UUID LANGUAGE sql STABLE AS $$
    SELECT COALESCE(
        (auth.jwt() ->> 'org_id')::UUID,
        NULL
    );
$$;

-- ----------------------------------------------------------
-- ORGANIZATIONS — a user can only see their own org
-- ----------------------------------------------------------
CREATE POLICY "org_select" ON organizations
    FOR SELECT USING (id = auth_org_id());

CREATE POLICY "org_update" ON organizations
    FOR UPDATE USING (id = auth_org_id());

-- ----------------------------------------------------------
-- LEADS
-- ----------------------------------------------------------
CREATE POLICY "leads_all" ON leads
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

-- ----------------------------------------------------------
-- CUSTOMERS
-- ----------------------------------------------------------
CREATE POLICY "customers_all" ON customers
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

-- ----------------------------------------------------------
-- SALES
-- ----------------------------------------------------------
CREATE POLICY "sales_all" ON sales
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

-- ----------------------------------------------------------
-- EXPENSES
-- ----------------------------------------------------------
CREATE POLICY "expenses_all" ON expenses
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

-- ----------------------------------------------------------
-- AUDIT REPORTS
-- ----------------------------------------------------------
CREATE POLICY "audit_all" ON audit_reports
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

-- ----------------------------------------------------------
-- INTEGRATIONS
-- ----------------------------------------------------------
CREATE POLICY "integration_connections_all" ON integration_connections
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

CREATE POLICY "integration_sync_runs_all" ON integration_sync_runs
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());

CREATE POLICY "integration_record_links_all" ON integration_record_links
    FOR ALL USING (org_id = auth_org_id())
    WITH CHECK (org_id = auth_org_id());
