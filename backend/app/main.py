from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1 import auth, chat, diseases, doctors, videos, appointments, schemes, admin

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(title=settings.APP_NAME, version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(diseases.router, prefix=settings.API_V1_PREFIX)
app.include_router(doctors.router, prefix=settings.API_V1_PREFIX)
app.include_router(videos.router, prefix=settings.API_V1_PREFIX)
app.include_router(appointments.router, prefix=settings.API_V1_PREFIX)
app.include_router(schemes.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
