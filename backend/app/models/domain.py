from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Date, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    mfa_secret = Column(String(100), nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    num_colegiado = Column(String(50), nullable=True)
    rol = Column(String(30), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

class ProductoEstupefaciente(Base):
    __tablename__ = "productos_estupefacientes"

    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_nacional = Column(String(20), unique=True, nullable=False, index=True)
    nombre_comercial = Column(String(100), nullable=False)
    principio_activo = Column(String(100), nullable=False)
    presentacion = Column(String(100), nullable=False)
    lista_estupefaciente = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True)

class LibroEstupefacientes(Base):
    __tablename__ = "libro_estupefacientes"

    id_movimiento = Column(BigInteger, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos_estupefacientes.id_producto"), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    num_lote = Column(String(50), nullable=False)
    fecha_caducidad = Column(Date, nullable=False)
    cantidad = Column(Integer, nullable=False)
    saldo_resultante = Column(Integer, nullable=False)
    doc_referencia = Column(String(100), nullable=False)
    prescriptor_destino = Column(String(150), nullable=True)
    motivo_ajuste = Column(Text, nullable=True)
    id_usuario_firma = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_usuario_aprobacion = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    estado = Column(String(20), default="CONFIRMADO", nullable=False)
    timestamp_servidor = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id_audit = Column(BigInteger, primary_key=True, index=True)
    tabla_afectada = Column(String(50), nullable=False)
    operacion = Column(String(20), nullable=False)
    id_registro_afectado = Column(BigInteger, nullable=True)
    id_usuario = Column(Integer, nullable=True)
    ip_origen = Column(String(45), nullable=True)
    timestamp_ntp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)