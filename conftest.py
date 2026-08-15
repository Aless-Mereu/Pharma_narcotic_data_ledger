import sys
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient

# En Windows, fijar SelectorEventLoop para compatibilidad con asyncpg/sockets
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture
async def client():
    # Test contra la API en vivo en Docker
    async with AsyncClient(base_url="http://localhost:8000", timeout=10.0) as ac:
        yield ac