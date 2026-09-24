from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker)

from src.core.config import settings


engine = create_async_engine(settings.db.url)

async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_session():
    
    async with async_session_factory() as session:
        yield session


