"""
Integration test fixtures.

Uses an in-memory SQLite DB rather than spinning up Postgres for every test
run — fast, no external dependency for CI's unit/integration tier. The
Postgres-specific CI job (docker-compose based) separately covers anything
that depends on Postgres-only features (e.g. native UUID/ENUM types), so this
isn't a full substitute for that, just the fast-feedback layer.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models import domain  # noqa: F401 ensures models are registered
from app.api.v1 import auth

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_otp_services(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.store = {}

        def setex(self, key, expiry, value):
            self.store[key] = value

        def get(self, key):
            return self.store.get(key)

        def delete(self, key):
            self.store.pop(key, None)

    fake_redis = FakeRedis()
    monkeypatch.setattr(auth.limiter, "enabled", False)
    monkeypatch.setattr(auth, "redis_client", fake_redis)
    monkeypatch.setattr(auth, "generate_otp", lambda: "123456")
    monkeypatch.setattr(auth, "send_otp_email", lambda email, otp: None)

    return fake_redis

@pytest.fixture(scope="function")
def client(db_session,mock_otp_services):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
