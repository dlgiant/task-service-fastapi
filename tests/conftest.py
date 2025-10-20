import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from app.models import Base
from app.database import get_db
from app.main import app
from httpx import AsyncClient
import os

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_taskdb.db"


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    # Clean up test database file
    if os.path.exists("./test_taskdb.db"):
        os.remove("./test_taskdb.db")


@pytest_asyncio.fixture
async def async_session(async_engine):
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
