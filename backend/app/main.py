import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.routers import auth, ledger

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pharma_api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para el Control y Libro Diligenciado Digital de Estupefacientes (GAMP 5 / Anexo 11)"
)

# Exception Handler Global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(f"Excepción no controlada en {request.url.path}: {str(exc)}\n{error_trace}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "detail": str(exc),
            "type": exc.__class__.__name__,
            "path": request.url.path
        }
    )

app.include_router(auth.router)
app.include_router(ledger.router)

@app.get("/health", tags=["Salud del Sistema"])
async def health_check():
    return {"status": "HEALTHY", "system": settings.PROJECT_NAME}