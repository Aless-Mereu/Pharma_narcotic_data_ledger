import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.routers import auth, ledger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pharma_api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema Digital Validado para Registro Inmutable del Libro Oficial de Estupefacientes (GAMP 5 / 21 CFR Part 11 / Anexo 11)",
    version="1.0.0"
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rutas API (Prioridad de coincidencia)
app.include_router(auth.router)
app.include_router(ledger.router)

@app.get("/health", tags=["Sistema"])
async def health_check():
    return {"status": "HEALTHY", "environment": settings.ENVIRONMENT, "gxp_compliant": True}

# 3. Montaje de Estáticos y Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))