# LBT OS — Deployment Guide

## Prerequisites

- Supabase project (free tier works for MVP)
- Clerk account + application
- Stripe account (test mode first)
- OpenAI API key
- Render / Railway / Fly.io account (backend)
- Vercel / Netlify account (frontend)

---

## 1. Database Setup (Supabase)

```bash
# In Supabase SQL Editor, run in order:
1. supabase/schema.sql
2. supabase/rls_policies.sql
```

**Key setting**: In Supabase → Settings → API → copy your:
- Project URL → `SUPABASE_URL`
- `service_role` key (secret) → `SUPABASE_SERVICE_KEY`

---

## 2. Clerk Setup

1. Create a new Clerk application
2. Enable **Organizations** in Clerk Dashboard → Organizations
3. Copy publishable key → `VITE_CLERK_PUBLISHABLE_KEY`
4. Copy secret key → `CLERK_SECRET_KEY`
5. Create a webhook pointing to `https://your-api.com/api/v1/billing/webhook`
   - Events: `organization.created`, `organization.deleted`
   - Copy signing secret → `CLERK_WEBHOOK_SECRET`

---

## 3. Stripe Setup

1. Create products and prices in Stripe Dashboard:
   - Basic: $29/month recurring
   - Pro: $79/month recurring
   - Premium: $149/month recurring
2. Copy price IDs → `STRIPE_PRICE_BASIC`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_PREMIUM`
3. Copy secret key → `STRIPE_SECRET_KEY`
4. Create webhook endpoint: `https://your-api.com/api/v1/billing/webhook`
   - Events: `customer.subscription.*`, `checkout.session.completed`
5. Copy signing secret → `STRIPE_WEBHOOK_SECRET`

---

## 4. Backend Deployment (Render recommended)

```bash
# 1. Create a new Web Service on Render
# 2. Connect your GitHub repo
# 3. Set:
#    Root Directory: lbt-os/backend
#    Build Command: pip install -r requirements.txt
#    Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# 4. Add all environment variables from .env.example
```

**Or with Docker:**
```bash
cd lbt-os/backend
docker build -t lbt-os-api .
docker run -p 8000:8000 --env-file .env lbt-os-api
```

---

## 5. Frontend Deployment (Vercel recommended)

```bash
# 1. Push to GitHub
# 2. Import project in Vercel
# 3. Set:
#    Root Directory: lbt-os/frontend
#    Build Command: npm run build
#    Output Directory: dist

# 4. Add environment variables:
VITE_CLERK_PUBLISHABLE_KEY=pk_live_...
VITE_API_URL=https://your-api.render.com
```

**Or local:**
```bash
cd lbt-os/frontend
cp .env.example .env    # fill in values
npm install
npm run dev
```

---

## 6. Local Development (Full Stack)

**Terminal 1 — Backend:**
```bash
cd lbt-os/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill in values
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd lbt-os/frontend
npm install
cp .env.example .env
npm run dev
```

API docs available at: `http://localhost:8000/docs` (dev mode only)

---

## 7. Post-Deployment Checklist

- [ ] Supabase schema applied
- [ ] RLS policies applied
- [ ] Clerk org ID syncing to organizations table (via first user onboarding)
- [ ] Stripe test checkout works end-to-end
- [ ] Stripe webhook events received and subscriptions syncing
- [ ] AI audit returns insights (test with 30 days of sample data)
- [ ] CORS origin set correctly in backend config
- [ ] `APP_ENV=production` set (disables /docs endpoint)
