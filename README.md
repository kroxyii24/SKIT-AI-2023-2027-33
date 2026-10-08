# JanSwasthya AI

**AI-Powered Public Health Awareness and Affordable Healthcare Access Platform for Indian Citizens**

A B.Tech final year project. Not a diagnostic tool — an education and access layer connecting Indian citizens (especially low-income and rural populations) to verified health information, government schemes, and real doctors.

## Core principle
The AI never diagnoses, never prescribes, and always defers to real healthcare professionals — enforced architecturally (confidence-gated RAG, hard-gated emergency detection, structured-data-first content for accuracy-critical information) rather than left to prompt-level good intentions alone.

## Repository structure
```
janswasthya-ai/
├── backend/           FastAPI application (Python)
│   ├── app/
│   │   ├── api/v1/        API routes
│   │   ├── core/          config, security, RBAC, rate limiting, i18n, prompt guard, audit
│   │   ├── models/        SQLAlchemy models
│   │   ├── schemas/       Pydantic request/response schemas
│   │   ├── services/      business logic — rag/, emergency/, content/
│   │   └── db/            session management
│   ├── alembic/        database migrations
│   └── tests/          unit, integration, and load tests
├── frontend/           Next.js application (TypeScript)
│   └── src/
│       ├── app/            pages (chat, login, register, admin, diseases, doctor-portal)
│       ├── components/     shared UI components
│       └── lib/            API client, auth store
├── infra/              docker-compose, Dockerfiles, Nginx config
├── docs/
│   ├── architecture/   diagrams, deployment guide, security checklist, testing plans
│   └── research/       problem statement through methodology (report-ready)
└── .github/workflows/  CI/CD pipelines
```

## Local development setup
```bash
# 1. Backend
cd backend
cp .env.example .env   # fill in real values — see docs/architecture/secrets-handling.md
pip install -r requirements.txt --break-system-packages
alembic upgrade head
uvicorn app.main:app --reload

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev

# 3. Full stack via Docker Compose (alternative to steps 1-2)
cd infra/docker
docker compose up
```

## Running tests
```bash
cd backend
pytest tests/ -v                    # unit + integration tests
locust -f tests/load/locustfile.py --host http://localhost:8000   # load test
```

## What's implemented (Milestones 1–46)
- ✅ Multilingual (EN/HI/Hinglish) RAG chat with confidence-gated generation and citation attachment
- ✅ Hard-gated emergency detection (pattern-based, runs before any LLM call)
- ✅ Prompt injection defense (pre-filter + structural prompt isolation)
- ✅ JWT + RBAC authentication across all roles (citizen, doctor, ASHA worker, admin)
- ✅ Doctor verification workflow (application → admin review → gated visibility)
- ✅ Educational video library with moderation gate
- ✅ Appointment booking with double-booking prevention
- ✅ Government health schemes module (structured data, not LLM-generated)
- ✅ Disease Explorer with structured, consistent disease information pages
- ✅ Admin dashboard (aggregate stats only, no raw PII exposure)
- ✅ Append-only audit logging on security-sensitive actions
- ✅ CI/CD pipeline (lint, test, Docker build) + deploy workflow stub
- ✅ RAG evaluation harness (groundedness + refusal-correctness scoring)
- ✅ Accessibility pass (WCAG 2.1 AA target, aria-live chat region, keyboard nav)
- ✅ Security testing checklist cross-referenced against actual implementation
- ✅ Full research documentation (problem statement → methodology → future scope)

## Known gaps (honest, not hidden)
- Live video consultation not implemented — booking-only in v1, architecture is video-ready
- Payment gateway for ₹20/₹50/₹100 tiers is not integrated — manual/mock in v1
- Only 3 of 9 target languages are content-verified and enabled; the rest are architected for but intentionally disabled until translated content is clinically reviewed
- Refresh token revocation list not implemented (tokens can't be invalidated before natural expiry)
- Load and security tests are built but not yet *executed* against a live deployment — that's the natural next step once hosting (Milestone 43 guide) is set up

## License / Academic use
Built as an academic project. Verify your institution's policy on AI-assisted development disclosure before submission — this project was built collaboratively with Claude (Anthropic) as a development partner across all layers of the stack, and that process is worth describing accurately in your report's methodology section rather than presenting the code as unassisted individual work.
