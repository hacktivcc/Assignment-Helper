from httpx import AsyncClient

class Client:
    def __init__(self):
        self.client = AsyncClient()
        
    async def get(self, url, headers=None):
        response = await self.client.get(url, headers=headers)
        return response.text

    async def post(self, url, headers=None, data=None):
        response = await self.client.post(url, headers=headers, data=data)
        return response.text

    async def put(self, url, headers=None, data=None):
        response = await self.client.put(url, headers=headers, data=data)
        return response.text
    
    async def patch(self, url, headers=None, data=None):
        response = await self.client.patch(url, headers=headers, data=data)
        return response.text
    
    async def delete(self, url, headers=None):
        response = await self.client.delete(url, headers=headers)
        return response.text
    
    async def head(self, url, headers=None):
        response = await self.client.head(url, headers=headers)
        return response.text
    
    async def options(self, url, headers=None):
        response = await self.client.options(url, headers=headers)
        return response.text
    
    async def close(self):
        await self.client.aclose()
