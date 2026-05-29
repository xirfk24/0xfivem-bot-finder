from sqlmodel import SQLModel, Field
from core.models.base_model import BaseModel


class GuildBase(SQLModel):

    guild_id: int
    guild_name: str

class Guild(GuildBase, BaseModel, table=True):

    __tablename__ = "guilds"

    guild_id: int = Field()
    guild_name: str = Field()
    announce_channel_id: int | None = Field(default=None, nullable=True)