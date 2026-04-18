# LBT OS — Marketplace Layer (Phase 2 Design)

## Concept

A location-based B2B/B2C marketplace connecting Denver-area businesses with
service providers — think Angi meets Tinder, built on top of the LBT OS platform.

## Why it works on top of LBT OS

Every business using LBT OS already has:
- A verified profile (via Clerk org)
- A track record (leads, sales, customer reviews)
- A service catalog (from the template engine)
- A paid subscription (trust signal)

The marketplace layer surfaces this data to consumers and other businesses.

---

## Data Model (additions to schema.sql)

```sql
-- Business public profiles
CREATE TABLE profiles (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID UNIQUE NOT NULL REFERENCES organizations(id),
    tagline      TEXT,
    description  TEXT,
    logo_url     TEXT,
    website      TEXT,
    services     TEXT[],          -- from template engine
    service_area TEXT,            -- "Denver Metro", "5 miles", etc.
    lat          DECIMAL(9,6),
    lng          DECIMAL(9,6),
    avg_rating   DECIMAL(3,2) DEFAULT 0,
    review_count INT DEFAULT 0,
    is_visible   BOOLEAN DEFAULT TRUE,  -- opt-in to marketplace
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Consumer/requester profiles (homeowners, businesses needing services)
CREATE TABLE requesters (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT,
    lat        DECIMAL(9,6),
    lng        DECIMAL(9,6),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Service requests (demand side)
CREATE TABLE service_requests (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID NOT NULL REFERENCES requesters(id),
    category     TEXT NOT NULL,       -- hvac, plumbing, etc.
    description  TEXT NOT NULL,
    urgency      TEXT DEFAULT 'flexible',  -- asap | today | this_week | flexible
    budget_min   DECIMAL(10,2),
    budget_max   DECIMAL(10,2),
    lat          DECIMAL(9,6),
    lng          DECIMAL(9,6),
    status       TEXT DEFAULT 'open',  -- open | matched | fulfilled | canceled
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Matches (AI-selected, Tinder-style)
CREATE TABLE matches (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id        UUID NOT NULL REFERENCES service_requests(id),
    org_id            UUID NOT NULL REFERENCES organizations(id),
    match_score       INT,            -- 0-100, AI-computed
    match_reasons     TEXT[],
    status            TEXT DEFAULT 'pending',  -- pending | accepted | declined | booked
    contacted_at      TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Reviews
CREATE TABLE reviews (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID NOT NULL REFERENCES organizations(id),
    requester_id UUID REFERENCES requesters(id),
    rating       INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body         TEXT,
    verified     BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

---

## AI Matching Engine

```python
# Pseudo-code for match scoring

def score_match(request: ServiceRequest, provider: OrgProfile) -> int:
    score = 0

    # 1. Category match (hard requirement)
    if request.category not in provider.services:
        return 0

    # 2. Distance (closer = higher score, 0-30 pts)
    distance_km = haversine(request.lat, request.lng, provider.lat, provider.lng)
    score += max(0, 30 - distance_km * 2)

    # 3. Ratings (0-25 pts)
    score += provider.avg_rating * 5

    # 4. LBT OS health score (pro signal — 0-20 pts)
    audit = get_latest_audit(provider.org_id)
    score += (audit.health_score / 100) * 20 if audit else 10

    # 5. Response time bonus (from LBT lead follow-up data — 0-15 pts)
    avg_follow_up_hours = get_avg_follow_up_time(provider.org_id)
    if avg_follow_up_hours < 1:   score += 15
    elif avg_follow_up_hours < 4: score += 10
    elif avg_follow_up_hours < 24: score += 5

    # 6. Capacity (active leads / sales volume indicates availability — 0-10 pts)
    recent_sales = get_recent_sale_count(provider.org_id, days=7)
    score += max(0, 10 - recent_sales // 5)

    return min(100, score)
```

---

## API Endpoints (Phase 2)

```
POST /api/v1/marketplace/profile          Create/update public profile
GET  /api/v1/marketplace/search           Search providers (category + location)
POST /api/v1/marketplace/request          Submit a service request
GET  /api/v1/marketplace/matches/{req_id} Get AI matches for a request
POST /api/v1/marketplace/matches/{id}/accept|decline
GET  /api/v1/marketplace/reviews/{org_id} Get reviews
POST /api/v1/marketplace/reviews          Submit a review (post-job)
```

---

## UX Flow

### Consumer (needs a service):
1. Describe job → category + description + budget + location
2. LBT AI selects top 3 providers (scored, ranked)
3. Consumer swipes or selects → instant connect (call/message/book)
4. After job: leave a review

### Provider (business on LBT OS):
1. Opts in to marketplace in settings
2. Receives match notifications (in-app + SMS)
3. Accepts/declines within 30 min (fast response = higher rank)
4. Job tracked back in LBT OS as a new lead automatically

---

## Monetization (Phase 2)

- **Lead fee**: $5-15 per accepted match (pay-per-lead model)
- **Boost**: $X/month to appear first in search results
- **Pro signal**: Pro/Premium LBT subscribers get priority matching rank

---

## Tech additions needed for Phase 2

- PostGIS extension on Supabase (for geospatial queries)
- Twilio or similar for SMS/push notifications
- Stripe Connect for provider payouts (if commission model)
- Separate consumer-facing React app or landing page
- Redis for caching match results
