import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db

from app.core.config import settings


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

if "test" not in TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL must point to a test database"
    )

test_engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session = TestingSessionLocal(bind=connection)

        yield session

        await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
            yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()