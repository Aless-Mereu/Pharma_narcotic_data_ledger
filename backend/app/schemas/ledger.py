from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
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
    model_config = ConfigDict(from_attributes=True)

    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    num_lote: str
    cantidad: int
    saldo_resultante: int
    doc_referencia: str
    estado: str
    timestamp_servidor: datetime

class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    num_lote: str
    fecha_caducidad: date
    cantidad: int
    saldo_resultante: int
    doc_referencia: str
    prescriptor_destino: Optional[str] = None
    motivo_ajuste: Optional[str] = None
    estado: str
    id_usuario_firma: int
    timestamp_servidor: datetime

class AuditTrailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_audit: int
    tabla_afectada: str
    operacion: str
    id_registro_afectado: int
    datos_previos: Optional[Dict[str, Any]] = None
    datos_nuevos: Optional[Dict[str, Any]] = None
    id_usuario_db: Optional[str] = None
    ip_origen: Optional[str] = None
    timestamp_ntp: datetime

class ProductStockSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    codigo_nacional: str
    nombre_comercial: str
    principio_activo: str
    presentacion: str
    lista_estupefaciente: str
    stock_actual: int
    total_entradas: int
    total_salidas: int
    total_ajustes_storno: int
    ultimo_movimiento: Optional[datetime] = None

class MovementTraceDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimiento: int
    timestamp_servidor: datetime
    tipo_movimiento: str
    cantidad: int
    saldo_resultante: int
    num_lote: str
    fecha_caducidad: date
    doc_referencia: str
    prescriptor_destino: Optional[str] = None
    motivo_ajuste: Optional[str] = None
    usuario_firma_nombre: str
    usuario_firma_rol: str