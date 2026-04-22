# LBT OS Security Best-Practices Report

Date: 2026-04-20

## Executive Summary

LBT OS is materially closer to production readiness. The prior audit items for CSV upload memory DoS, CSV extension spoofing, CSV formula injection, Stripe webhook idempotency, LLM route rate limiting, and production Clerk audience enforcement are covered by code and regression tests. This pass also hardened the newer Signal Desk surface, production host/CORS configuration, Stripe plan handling, and frontend reverse-tabnabbing behavior.

Remaining production risk is mostly configuration and launch operations: real Stripe live/test keys, webhook setup, Clerk JWT audience, trusted hosts, Supabase RLS/storage policies, monitoring, and live smoke testing.

## Findings And Fixes

### Fixed: Production Host And CORS Hardening

Risk: Medium. Production CORS previously carried development localhost origins, and the API did not enforce trusted Host headers.

Fix:
- Production CORS now uses `CORS_ORIGINS` or `FRONTEND_URL`; localhost origins are development-only.
- `TrustedHostMiddleware` is enabled.
- Production fails fast unless `TRUSTED_HOSTS` is set.
- FastAPI docs and OpenAPI schema are disabled in production.

References:
- `backend/app/config.py:84`
- `backend/app/config.py:98`
- `backend/app/main.py:29`
- `backend/app/main.py:35`

### Fixed: Signal Desk Upload Spoofing And Storage Safety

Risk: High. Message attachments accepted broad MIME values and did not verify signatures deeply enough, which can allow renamed binary files to be stored as safe document/image types.

Fix:
- Attachment extension must be supported.
- MIME type must match the extension.
- File signatures are checked for PDF, images, video containers, and Office formats.
- `application/octet-stream` is only accepted for signed Office document formats.
- Filenames are sanitized before Supabase storage paths are generated.
- Uploads verify the channel belongs to the organization before storage.

References:
- `backend/app/services/messaging.py:41`
- `backend/app/services/messaging.py:505`
- `backend/app/services/messaging.py:535`

### Fixed: Signal Desk Input And LLM Abuse Controls

Risk: Medium. Normal channel messages can trigger bot mentions, which can call LLMs. Loose message types and unlimited attachment IDs also increase abuse surface.

Fix:
- Message content and AI questions are capped at 4,000 characters.
- Message attachments are capped at five file IDs.
- User-submitted message types are restricted to `text` and `gif`.
- Channel message posts are rate-limited to `30/minute`.
- Direct Signal Desk AI ask remains rate-limited to `20/hour`; file uploads are rate-limited to `20/hour`; exports are `10/hour`.
- Unsupported internal message types are rejected at the service layer.

References:
- `backend/app/models/messages.py:13`
- `backend/app/routers/messages.py:77`
- `backend/app/routers/messages.py:147`
- `backend/app/routers/messages.py:178`
- `backend/app/services/messaging.py:326`

### Fixed: Stripe Checkout/Portal Robustness

Risk: Medium. Unsupported checkout plans could fall through as server errors, and the billing portal returned outside the authenticated app path.

Fix:
- Checkout plans are allow-listed to `basic`, `pro`, and `premium`.
- Expected Stripe configuration errors return `400` instead of accidental `500`.
- Billing portal return URL now points back to `/app/billing`.
- Production startup validates Stripe secret key, webhook secret, and price ID shapes.
- Existing webhook idempotency remains in place through stored Stripe event IDs.

References:
- `backend/app/config.py:117`
- `backend/app/routers/stripe_webhooks.py:31`
- `backend/app/routers/stripe_webhooks.py:40`
- `backend/app/routers/stripe_webhooks.py:62`
- `backend/app/routers/stripe_webhooks.py:87`

### Fixed: Frontend Reverse-Tabnabbing

Risk: Low. Programmatic signed-file downloads used `_blank` without `noopener`.

Fix:
- Added `rel="noopener noreferrer"` to the generated file-download anchor.

Reference:
- `frontend/src/pages/Messages.jsx:721`

## Previously Confirmed Fixed

- CSV upload memory DoS: bounded upload reads and regression test.
- CSV file extension spoofing: route rejects spoofed CSV filenames and regression test.
- CSV formula injection: formula-leading cells are neutralized and regression test.
- Stripe webhook idempotency: duplicate event IDs are ignored and regression test.
- LLM endpoint rate limiting: audit, strategy, revenue-intelligence, and Signal Desk LLM entry points are limited.
- Clerk JWT audience: production fails fast unless audience enforcement is configured.

## Production Path To Revenue

1. Set production environment:
   - `APP_ENV=production`
   - `FRONTEND_URL=https://your-domain.com`
   - `CORS_ORIGINS=https://your-domain.com`
   - `TRUSTED_HOSTS=api.your-domain.com,your-render-host.onrender.com` or the exact deployment hosts
   - `CLERK_JWT_AUDIENCE=<your Clerk JWT audience>`
   - `DEMO_ALLOW_UNLIMITED_AUDITS=false`
   - `AUDIT_RATE_LIMIT=5/hour`

2. Configure Stripe:
   - Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_BASIC`, `STRIPE_PRICE_PRO`, and `STRIPE_PRICE_PREMIUM`.
   - In Stripe Dashboard, create a webhook endpoint pointing to `https://<api-host>/api/v1/billing/webhook`.
   - Subscribe the webhook to `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, and `checkout.session.completed`.
   - Run one Stripe test-mode Checkout end-to-end and confirm the org plan updates after the webhook.

3. Configure Clerk:
   - Create/verify the JWT template audience.
   - Confirm the frontend uses the same Clerk publishable key environment as the backend.
   - Add the production frontend URL to Clerk allowed redirect/origin settings.

4. Apply database and storage migrations:
   - Base schema, messages, message storage bucket, Signal Desk analytics/notifications, Stripe events, integrations, CSV import logs, revenue intelligence, and audit report fields.
   - Confirm Supabase storage bucket `message-files` exists and is private.
   - Confirm RLS/storage policies do not expose files across organizations.

5. Deploy and smoke test buttons:
   - Sign up/sign in.
   - Create or load demo workspace.
   - Add lead, sale, customer, and expense.
   - Run AI Audit.
   - Open Signal Desk, create channel, send message, mention `@BI`, upload/download allowed attachment.
   - Import CSV.
   - Start Stripe Checkout and return to `/app/billing`.
   - Open billing portal after a customer exists.

6. Add launch observability:
   - Backend error monitoring.
   - Stripe webhook logs.
   - Supabase database/storage logs.
   - Basic uptime check for `/health`.
   - Alert on failed integration syncs and failed AI/audit calls.

## Verification Run

- `frontend`: `npm run build` passed.
- `backend`: `python -m compileall app` passed.
- `backend`: `python -m unittest discover tests -v` passed, 15 tests.

Note: Live payment processing cannot be fully verified from local code alone. It requires real Stripe test or live keys, the configured webhook signing secret, a public HTTPS API URL, and a test Checkout completion in Stripe.
