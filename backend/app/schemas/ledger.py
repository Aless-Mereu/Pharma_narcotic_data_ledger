from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


# Esquema para login
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str = Field(..., min_length=6, max_length=6, description="Código de 6 dígitos MFA")


# Esquemas del Libro GxP
class MovementCreate(BaseModel):
    id_producto: int
    tipo_movimiento: str = Field(..., pattern="^(ENTRADA|SALIDA|AJUSTE_MERMA|STORNO)$")
    num_lote: str = Field(..., min_length=2, max_length=50)
    fecha_caducidad: date
    cantidad: int = Field(..., gt=0, description="Cantidad a mover (debe ser positiva)")
    doc_referencia: str = Field(..., min_length=2, max_length=100)
    prescriptor_destino: Optional[str] = None
    motivo_ajuste: Optional[str] = None

    # Campos de Re-Autenticación (Firma Electrónica)
    signature_password: str = Field(..., description="Contraseña personal para la firma del registro")
    signature_totp: str = Field(..., min_length=6, max_length=6, description="Código TOTP para firma GxP")


class MovementResponse(BaseModel):
    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    num_lote: str
    cantidad: int
    saldo_resultante: int
    doc_referencia: str
    estado: str
    timestamp_servidor: datetime

    class Config:
        from_attributes = True