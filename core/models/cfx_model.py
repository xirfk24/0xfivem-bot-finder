from sqlmodel import SQLModel, Field

from core.models.base_model import BaseModel


class CFXBase(SQLModel):

    server_address: str
    server_name: str
    initial: str

class CFX(CFXBase, BaseModel, table=True):

    __tablename__ = 'cfxs'

    server_address: str = Field(nullable=False)
    server_name: str = Field(nullable=False)
    initial: str = Field(nullable=False)