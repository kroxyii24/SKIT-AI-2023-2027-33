# Deployment Guide

## Architecture
```
User → Cloudflare (DNS, WAF, CDN, TLS) → Nginx (reverse proxy, security headers,
       rate limiting) → [FastAPI backend | Next.js frontend] → Postgres/Redis/Qdrant
```

## Recommended hosting for a B.Tech project budget: Render
Render is recommended over raw AWS for this project because:
- Free/low-cost tiers exist for Postgres, Redis, and web services — appropriate for a student project budget.
- Native Docker support (uses the `Dockerfile`s already built in Milestone 29) — no need to hand-configure EC2/ECS.
- Built-in HTTPS, no manual cert management needed if not using a custom domain via Cloudflare.

AWS is documented as an alternative for anyone wanting the deployment experience on their resume (ECS Fargate + RDS + ElastiCache + S3), but is meaningfully more setup work — recommend only if you have time budget beyond the 10 months for infra learning curve.

## Steps (Render)
1. **Database**: Create a Render PostgreSQL instance. Copy its internal connection string into `DATABASE_URL`.
2. **Redis**: Create a Render Redis instance (or use Upstash's free tier as an alternative).
3. **Qdrant**: Either self-host via a Render Docker service using the official `qdrant/qdrant` image, or use Qdrant Cloud's free tier (simpler — no infra to manage for the vector DB specifically).
4. **Backend service**: New Render "Web Service" → connect the GitHub repo → set root directory to `backend/` → Render auto-detects the `Dockerfile`. Add all vars from `.env.example` in Render's environment settings (never commit the real `.env`).
5. **Frontend service**: New Render "Web Service" → root directory `frontend/` → set `NEXT_PUBLIC_API_BASE_URL` to the backend service's public URL + `/api/v1`.
6. **Run migrations**: After first deploy, run `alembic upgrade head` via Render's shell access (or as a Render "Job").
7. **Custom domain + Cloudflare**: Point your domain's DNS to Render via Cloudflare (orange-cloud proxied), set Cloudflare SSL mode to "Full (strict)" once Render's TLS cert is issued.

## Nginx's role in this setup
On Render, Render's own edge already handles TLS termination and basic routing, so the `infra/nginx/nginx.conf` built in this milestone is primarily useful if:
- Self-hosting on a VPS/AWS EC2 instead of Render (then Nginx is the actual reverse proxy in front of the Docker Compose stack), or
- Wanting the security headers + rate limiting layer even behind Render (deploy Nginx as a sidecar in front of the backend service).

Document which path you actually take in your final report — this guide covers both so you aren't locked into a decision before you've tested actual hosting costs/limits against your usage.

## Post-deploy checklist
- [ ] `GET /health` returns 200 from the public URL
- [ ] Alembic migrations applied (`alembic current` shows `0002_audit_logs`)
- [ ] CORS `ALLOWED_ORIGINS` updated to the real frontend domain (not `localhost`)
- [ ] `JWT_SECRET_KEY` is a freshly generated production value, not the dev placeholder
- [ ] Rate limiting confirmed active (send >30 requests/min and confirm 429 response)
