from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum

class TipoMovimientoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE_STORNO = "AJUSTE_STORNO"
    AJUSTE_MERMA = "AJUSTE_MERMA"

class EstadoMovimientoEnum(str, Enum):
    BORRADOR = "BORRADOR"
    CONFIRMADO = "CONFIRMADO"
    ANULADO = "ANULADO"

class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None

class MovementCreate(BaseModel):
    id_producto: int
    tipo_movimiento: TipoMovimientoEnum
    num_lote: str = Field(..., max_length=50)
    fecha_caducidad: date
    cantidad: int = Field(..., gt=0, description="Cantidad positiva a mover")
    doc_referencia: str = Field(..., max_length=100)
    prescriptor_destino: Optional[str] = Field(None, max_length=150)
    motivo_ajuste: Optional[str] = Field(None, max_length=255)
    signature_password: str = Field(..., description="Contraseña de re-autenticación GxP")
    signature_totp: str = Field(..., description="Código TOTP para firma electrónica")

class StornoRequest(BaseModel):
    id_movimiento_original: int = Field(..., description="ID del movimiento que se desea anular/compensar")
    motivo_ajuste: str = Field(..., min_length=15, max_length=255, description="Justificación obligatoria de la anulación")
    signature_password: str = Field(..., description="Contraseña de re-autenticación GxP")
    signature_totp: str = Field(..., description="Código TOTP para firma electrónica")

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