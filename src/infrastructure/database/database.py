from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.api.core.config import settings


DATABASE_URL = settings.get_db_url()
DATABASE_URL_MIGR = settings.get_db_url_migr()

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)