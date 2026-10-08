"""
Single shared slowapi Limiter instance.

Must be imported (not re-instantiated) everywhere rate limiting is used —
slowapi ties its storage and exception handling to one Limiter bound to
app.state.limiter. Defining a second Limiter() in another module would
silently create disconnected rate-limit state.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
