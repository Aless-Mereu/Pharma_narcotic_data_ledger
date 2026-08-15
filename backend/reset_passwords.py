import asyncio
import bcrypt
from sqlalchemy import update
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.domain import Usuario


async def main():
    raw_pass = "GxPPass2026!".encode('utf-8')
    hashed = bcrypt.hashpw(raw_pass, bcrypt.gensalt(12)).decode('utf-8')

    async with AsyncSessionLocal() as session:
        # Actualizar usuarios iniciales
        for username in ["farmaceutico_regente", "director_tecnico"]:
            await session.execute(
                update(Usuario)
                .where(Usuario.username == username)
                .values(password_hash=hashed)
            )
        await session.commit()
    print("Contraseñas y hashes sincronizados correctamente en la BBDD.")


if __name__ == "__main__":
    asyncio.run(main())