from pydantic import BaseModel
from datetime import (
    datetime, timezone
)
from typing import (
    Type, List, Generic, TypeVar, Optional
)
from sqlmodel import (
    func, select, insert, update, delete, SQLModel
)
from sqlmodel.sql.expression import Select
from core.database import database


ModelType = TypeVar('ModelType', bound=SQLModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
T = TypeVar('T', bound=SQLModel)


class BaseRepo(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):

        self.db = database
        self.model = model
    
    async def create(self, data: CreateSchemaType | ModelType | dict) -> Optional[ModelType]:

        now = datetime.now(timezone.utc)
        data.update({'created_at': now, 'updated_at': now})
        return await self.db.execute(insert(self.model).values(**data))
    
    async def update(self, id: int, data: UpdateSchemaType | ModelType | dict) -> bool:
        data['updated_at'] = datetime.now(timezone.utc)
        return await self.db.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
    
    async def get(self, id: int) -> Optional[ModelType]:
        return await self.db.fetch_one(
            select(self.model).where(self.model.id == id)
        )
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        query: Optional[T | Select[T]] = None
    ) -> Optional[List[ModelType]]:
        if not query:
            query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        
        return await self.db.fetch_all(query)
    
    async def count(self, query: Optional[T | Select[T]] = None) -> int:
        return await self.db.fetch_val(
            select(func.count()).select_from(select(self.model).subquery())
        ) or 0
    
    async def delete(self, id: int) -> Optional[ModelType]:

        return await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )