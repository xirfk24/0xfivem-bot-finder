import re
import httpx

            
class CFXService:

    def __init__(self, address: str):
        self.address = f'http://{address}'
    
    async def getPlayers(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(f'{self.address}/players.json', headers={'User-Agent': 'CitizenFX/1'})
            return res.json()
    
    async def getInfo(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(f'{self.address}/info.json', headers={'User-Agent': 'CitizenFX/1'})
            return res.json()