# the file configures the db connection for the app

from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass

async def get_db():
   async with SessionLocal() as db:
       yield db