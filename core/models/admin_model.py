from sqlmodel import SQLModel, Field
from core.models.base_model import BaseModel


class AdminBase(SQLModel):

    discord_id: int

class Admin(AdminBase, BaseModel, table=True):

    __tablename__ = 'admins'

    discord_id: int = Field(nullable=False)