# Load Testing Plan

## Tooling
Locust (`tests/load/locustfile.py`) — chosen over k6/JMeter for Python-native scenario scripting, matching the backend's stack (easier for the same team to maintain).

## Test scenarios
1. **Baseline load**: 100 concurrent users, 10 min ramp — validates normal expected traffic (campus/pilot-deployment scale).
2. **Spike test**: 500 concurrent users ramped over 1 min — simulates a viral moment (e.g. shared during a health awareness campaign or after local news coverage).
3. **Soak test**: 50 concurrent users sustained for 2 hours — catches memory leaks, connection pool exhaustion, and gradual DB connection creep that short tests miss.

## Targets (v1 acceptance thresholds)
| Endpoint | p95 latency target | Notes |
|---|---|---|
| `GET /diseases/`, `/schemes/`, `/videos/` | < 200ms | Structured-data reads, should be fast and cacheable |
| `POST /auth/login` | < 300ms | bcrypt hashing is intentionally slow; budget for it |
| `POST /chat/message` (emergency path) | < 150ms | No LLM call on this path — should be near-instant |
| `POST /chat/message` (RAG path) | < 4s | Dominated by LLM generation latency — the real bottleneck to watch |

## Known bottleneck: RAG chat path
The embedding model and LLM call are the most expensive operations by far. Mitigations to test:
- Redis caching of embeddings for frequently-asked questions (not yet implemented — flagged as a post-load-test optimization if p95 exceeds target).
- Connection pooling limits on the vector DB client under concurrent load.
- Rate limiting (already in place, `RATE_LIMIT_PER_MINUTE`) as a backstop against a single client monopolizing LLM capacity.

## Running it
```bash
locust -f tests/load/locustfile.py --host http://localhost:8000
```
Then open the Locust web UI (default `http://localhost:8089`) to configure user count and ramp rate, and to view live latency/failure-rate graphs.

## What this milestone does NOT cover
Actual load test *execution* and result analysis — that requires a running backend + database + LLM endpoint, none of which exist in this sandbox. This delivers the tooling and the acceptance criteria; running it against your deployed environment and recording results is a task for later in the project, once Milestone 44 (deployment) is live.
