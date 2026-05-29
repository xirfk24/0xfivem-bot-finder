from sqlmodel import select
from core.repo.base import BaseRepo
from core.models.guild_model import (
    GuildBase, Guild
)


class IGuildCreate(GuildBase):
    pass

class IGuildUpdate(GuildBase):
    pass


class GuildRepo(BaseRepo[Guild, IGuildCreate, IGuildUpdate]):

    async def get_by_guild_id(self, guild_id: int) -> Guild | None:
        """Get guild by Discord guild_id"""
        query = select(Guild).where(Guild.guild_id == guild_id)
        return await self.db.fetch_one(query)

    async def get_all_with_announce_channel(self) -> list[Guild]:
        """Get all guilds that have announce_channel_id configured"""
        query = select(Guild).where(Guild.announce_channel_id.is_not(None))
        return await self.db.fetch_all(query) or []

    async def set_announce_channel(self, guild_id: int, channel_id: int | None) -> bool:
        """Set or update announce_channel_id for a guild"""
        guild = await self.get_by_guild_id(guild_id)
        if guild:
            return await self.update(guild.id, {'announce_channel_id': channel_id})
        return False


guild = GuildRepo(Guild)
