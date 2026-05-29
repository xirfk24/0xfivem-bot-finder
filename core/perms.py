import interactions
from core.repo import admin

async def is_admin(ctx: interactions.BaseContext) -> bool:
    return await admin.is_admin(ctx.author.id)