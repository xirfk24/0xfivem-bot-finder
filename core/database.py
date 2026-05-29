import databases
from core.settings import settings

from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(settings.DATABASE_URL)

database = databases.Database(settings.DATABASE_URL)