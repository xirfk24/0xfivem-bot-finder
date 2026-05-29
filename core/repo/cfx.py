from typing import Optional
from sqlmodel import (
    select
)

from core.repo.base import BaseRepo
from core.models.cfx_model import (
    CFXBase, CFX
)


class ICfxCreate(CFXBase):
    pass

class ICfxUpdate(CFXBase):
    pass


class CfxRepo(BaseRepo[CFX, ICfxCreate, ICfxUpdate]):

    async def get_initial(self, initial: str) -> Optional[CFX]:
        query = select(CFX).where(CFX.initial == initial)
        result = await self.db.fetch_one(query)
        return result

    async def get_address(self, address: str) -> Optional[CFX]:
        
        query = select(CFX).where(CFX.server_address == address)
        result = await self.db.fetch_one(query)
        return result

cfx = CfxRepo(CFX)