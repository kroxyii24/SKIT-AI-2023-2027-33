# Security Testing Checklist

Unlike a generic security checklist, every item below is checked against the *actual code built in this project* — pointing to the specific file that implements (or needs to implement) the control, so this doubles as a self-audit.

## Authentication & Authorization
| Check | Status | Reference |
|---|---|---|
| Passwords hashed with bcrypt, never stored plain | ✅ Implemented | `app/core/security.py` — `pwd_context = CryptContext(schemes=["bcrypt"])` |
| JWTs signed, expire, and are verified server-side | ✅ Implemented | `app/core/security.py`, `app/core/rbac.py` |
| RBAC enforced at the route level, not just UI hints | ✅ Implemented | `require_role()` dependency used in `admin.py`, `videos.py`, `doctors.py` |
| Login brute-force protection | ✅ Implemented | `10/minute` limit on `/auth/login` (Milestone 27) |
| Registration abuse protection | ✅ Implemented | `5/hour` limit on `/auth/register` |
| **TODO before production**: refresh token rotation/revocation list | ⚠️ Not yet implemented | Currently refresh tokens are stateless and can't be revoked before expiry — acceptable for a v1 demo, flagged as a real gap for production use |

## Injection Attacks
| Check | Status | Reference |
|---|---|---|
| SQL injection prevention | ✅ Implemented | All queries use SQLAlchemy's parameterized query builder (`select()`, `.where()`) — no raw string-interpolated SQL anywhere in the codebase |
| Prompt injection defense on LLM input | ✅ Implemented | `app/core/prompt_guard.py` — pattern pre-filter + structural isolation in `generation.py`'s prompt template |
| XSS prevention | ✅ Implemented (frontend) | React escapes rendered content by default; no `dangerouslySetInnerHTML` used anywhere in the frontend codebase — verify this holds as more pages are added |

## CSRF
| Check | Status | Reference |
|---|---|---|
| CSRF protection | ⚠️ Partially addressed | JWT-in-header (not cookie) auth is inherently CSRF-resistant since the token isn't automatically attached by the browser — no separate CSRF token needed *as long as* tokens stay in `localStorage`/memory and are never moved to cookies. **If cookie-based auth is ever added, CSRF tokens become mandatory** — flag this explicitly for whoever touches auth next. |

## Rate Limiting & DoS
| Check | Status | Reference |
|---|---|---|
| Global rate limit | ✅ Implemented | `slowapi`, `RATE_LIMIT_PER_MINUTE` in `app/core/rate_limit.py` |
| Endpoint-specific stricter limits | ✅ Implemented | Auth endpoints (Milestone 27) |
| Nginx-layer rate limiting (defense in depth) | ✅ Implemented | `infra/nginx/nginx.conf` `limit_req_zone` |
| Message length limits (context-stuffing prevention) | ✅ Implemented | `MAX_MESSAGE_LENGTH = 2000` in `prompt_guard.py` |

## Data Exposure
| Check | Status | Reference |
|---|---|---|
| Admin analytics returns aggregates only, not raw PII | ✅ Implemented | `app/api/v1/admin.py` — `/admin/stats` returns counts only |
| Doctor/video visibility gated correctly | ✅ Implemented | Public endpoints filter `is_verified_by_admin`/`is_approved` server-side, not client-side |
| Appointment visibility scoped per-user | ✅ Implemented | `appointments.py` `my_appointments()` filters by `patient_id`/`doctor_id` matching the authenticated user |
| Secrets never in source control | ✅ Implemented | `.gitignore` excludes `.env`; `.env.example` has placeholders only |

## Audit & Accountability
| Check | Status | Reference |
|---|---|---|
| Security-sensitive actions logged | ⚠️ Partial | `doctor.verify` and `video.approve` are logged (Milestones 25, 44). **TODO**: extend `log_action()` calls to `user.login` and `appointment.status_update` before final submission. |

## Recommended manual penetration testing pass (before demo/submission)
1. Attempt to access `/admin/*` routes with a non-admin JWT — confirm 403.
2. Attempt to book two appointments in the same doctor slot simultaneously (race condition check on the double-booking prevention logic in `appointments.py`).
3. Send the injection patterns from `prompt_guard.py`'s test suite manually through the actual chat UI (not just unit tests) to confirm the sanitization also works end-to-end through the frontend.
4. Try registering with an already-used phone number via a raw `curl` request (bypassing frontend validation) — confirm the backend still rejects it (frontend validation isn't a security control).
