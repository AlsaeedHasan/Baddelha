import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

load_dotenv()

# Set up test database URL before importing app modules
base_url = os.getenv("DATABASE_URL")
if base_url and "sqlite" not in base_url:
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", f"{base_url}_test")
else:
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL", "postgresql://postgres:postgres@db:5432/test_baddelha"
    )

from app.core.config import settings

settings.DATABASE_URL = TEST_DATABASE_URL

from app.core.database import Base, get_db
from app.items.models import Item
from app.main import app
from app.swaps.models import Swap
from app.users.models import User


@pytest.fixture(scope="session")
def engine():
    from sqlalchemy.pool import StaticPool

    if "sqlite" in TEST_DATABASE_URL:
        _engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(TEST_DATABASE_URL)

    # Recreate the database from scratch (skip for in-memory SQLite)
    if _engine.url.drivername != "sqlite":
        _engine.dispose()

        # Kill other active connections if Postgres is being used
        if "postgres" in _engine.url.drivername:
            import sqlalchemy

            default_url = _engine.url.set(database="postgres")
            try:
                with sqlalchemy.create_engine(
                    default_url, isolation_level="AUTOCOMMIT"
                ).connect() as conn:
                    conn.execute(
                        sqlalchemy.text(
                            f"SELECT pg_terminate_backend(pid) "
                            f"FROM pg_stat_activity "
                            f"WHERE datname = '{_engine.url.database}' "
                            f"AND pid <> pg_backend_pid();"
                        )
                    )
            except Exception:
                pass

        if database_exists(_engine.url):
            drop_database(_engine.url)
        create_database(_engine.url)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    yield _engine

    # Teardown the database setup after session
    Base.metadata.drop_all(bind=_engine)
    if _engine.url.drivername != "sqlite":
        _engine.dispose()

        if "postgres" in _engine.url.drivername:
            import sqlalchemy

            default_url = _engine.url.set(database="postgres")
            try:
                with sqlalchemy.create_engine(
                    default_url, isolation_level="AUTOCOMMIT"
                ).connect() as conn:
                    conn.execute(
                        sqlalchemy.text(
                            f"SELECT pg_terminate_backend(pid) "
                            f"FROM pg_stat_activity "
                            f"WHERE datname = '{_engine.url.database}' "
                            f"AND pid <> pg_backend_pid();"
                        )
                    )
            except Exception:
                pass

        drop_database(_engine.url)


@pytest.fixture(scope="function")
def db_session(engine):
    # Use nested transactions/savepoints so each test starts fresh
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    # Roll back after the test completes to discard any DB mutations from the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as _client:
        yield _client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_factories(db_session):
    from tests.factories import (
        ChatRoomFactory,
        CommentFactory,
        ItemFactory,
        MessageFactory,
        SwapFactory,
        UserFactory,
    )

    for factory_cls in (
        UserFactory,
        ItemFactory,
        CommentFactory,
        SwapFactory,
        ChatRoomFactory,
        MessageFactory,
    ):
        factory_cls._meta.sqlalchemy_session = db_session
    yield


from app.core.security import create_access_token
from tests.factories import UserFactory


@pytest.fixture
def auth_headers(db_session):
    user = UserFactory()
    access_token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {access_token}"}, user


@pytest.fixture
def user_client(client, auth_headers):
    headers, user = auth_headers
    client.headers.update(headers)
    return client, user
