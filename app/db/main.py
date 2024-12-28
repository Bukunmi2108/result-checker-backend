from sqlmodel import create_engine, text, SQLModel 
from sqlalchemy.ext.asyncio import AsyncEngine
from app.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = AsyncEngine(
    create_engine(
        url=settings.DATABASE_URL
    )
)

async def init_db():
    async with engine.begin() as conn:
        from app.models import Admin, ExamCentre, Student, User, RevokedToken

        await conn.run_sync(SQLModel.metadata.create_all)

from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:

    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session