from fastapi import FastAPI
from backend.app.core.config import settings
from backend.app.routers import auth, ledger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para el Control y Libro Diligenciado Digital de Estupefacientes (GAMP 5 / Anexo 11)"
)

app.include_router(auth.router)
app.include_router(ledger.router)

@app.get("/health", tags=["Salud del Sistema"])
async def health_check():
    return {"status": "HEALTHY", "system": settings.PROJECT_NAME}