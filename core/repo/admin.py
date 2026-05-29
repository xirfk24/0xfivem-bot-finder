from sqlmodel import select
from core.repo.base import BaseRepo
from core.models.admin_model import (
    AdminBase, Admin
)


class IAdminCreate(AdminBase):
    pass

class IAdminUpdate(AdminBase):
    pass


class AdminRepo(BaseRepo[Admin, IAdminCreate, IAdminUpdate]):

    async def is_admin(self, discord_id: int) -> bool | None:

        query = select(Admin).where(Admin.discord_id == discord_id)
        return await self.db.fetch_one(query)


admin = AdminRepo(Admin)