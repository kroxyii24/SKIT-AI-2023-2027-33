# Secrets & Credentials Handling

## Rules
1. **Never commit `.env`** — it's already in `.gitignore`. Only `.env.example` (with placeholder values) is committed.
2. **JWT_SECRET_KEY** must be a high-entropy random string, unique per environment (dev/staging/prod never share one). Rotating it invalidates all existing tokens — plan rotations accordingly.
3. **Database credentials**: in production, injected via the hosting platform's secret manager (Render/AWS Secrets Manager), never hardcoded in `docker-compose.yml` beyond local dev defaults.
4. **LLM API keys** (if using a hosted provider instead of self-hosted): same rule — environment-injected only, never in source control, never logged. `app/services/rag/generation.py` intentionally does not log the API key or full request payload.
5. **Object storage credentials** (for video/PDF uploads, added Milestone 34+): same pattern — scoped IAM credentials with least-privilege (write-only to the specific bucket, no account-wide access).

## What to do if a secret leaks
1. Rotate it immediately at the source (regenerate JWT secret, rotate DB password, revoke+reissue API key).
2. Force-invalidate existing sessions if JWT_SECRET_KEY leaked (all tokens signed with the old key become invalid automatically once rotated — no separate revocation list needed given our short-lived access tokens + refresh token design).
3. Audit `audit_logs` table for suspicious activity in the affected window.

## CI/CD secrets
GitHub Actions secrets (Settings → Secrets and variables → Actions) are used for the `deploy.yml` workflow once a hosting provider is finalized (Milestone 44). Never echo secret values in workflow logs — GitHub automatically masks values that exactly match a registered secret, but constructing a secret value from parts (e.g. concatenation) defeats this masking, so avoid that pattern.
