import io
import csv
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_db
from backend.app.core.security import verify_password, verify_totp_code
from backend.app.models.domain import LibroEstupefacientes, Usuario, AuditTrail
from backend.app.schemas.ledger import (
    MovementCreate,
    MovementResponse,
    StornoRequest,
    TipoMovimientoEnum,
    LedgerEntryResponse,
    AuditTrailResponse
)
from backend.app.routers.auth import get_current_user

logger = logging.getLogger("pharma_api")
router = APIRouter(prefix="/ledger", tags=["Libro Oficial de Estupefacientes"])


@router.post("/movement", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
        movement_in: MovementCreate,
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. Validación de Firma Electrónica
    if not verify_password(movement_in.signature_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma rechazada: Contraseña incorrecta"
        )

    if not verify_totp_code(current_user.mfa_secret, movement_in.signature_totp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma rechazada: Código MFA inválido"
        )

    # 2. Obtener saldo anterior
    query_last = (
        select(LibroEstupefacientes)
        .where(LibroEstupefacientes.id_producto == movement_in.id_producto)
        .order_by(LibroEstupefacientes.id_movimiento.desc())
        .limit(1)
    )
    result_last = await db.execute(query_last)
    ultimo_registro = result_last.scalar_one_or_none()

    saldo_anterior = ultimo_registro.saldo_resultante if ultimo_registro else 0

    # 3. Calcular saldo resultante
    if movement_in.tipo_movimiento == TipoMovimientoEnum.ENTRADA:
        saldo_nuevo = saldo_anterior + movement_in.cantidad
    elif movement_in.tipo_movimiento == TipoMovimientoEnum.SALIDA:
        if saldo_anterior < movement_in.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo actual: {saldo_anterior}, Cantidad solicitada: {movement_in.cantidad}"
            )
        saldo_nuevo = saldo_anterior - movement_in.cantidad
    else:
        saldo_nuevo = saldo_anterior

    # 4. Asentar registro inmutable
    nuevo_movimiento = LibroEstupefacientes(
        id_producto=movement_in.id_producto,
        tipo_movimiento=movement_in.tipo_movimiento.value,
        num_lote=movement_in.num_lote,
        fecha_caducidad=movement_in.fecha_caducidad,
        cantidad=movement_in.cantidad,
        saldo_resultante=saldo_nuevo,
        doc_referencia=movement_in.doc_referencia,
        prescriptor_destino=movement_in.prescriptor_destino,
        motivo_ajuste=movement_in.motivo_ajuste,
        id_usuario_firma=current_user.id_usuario,
        estado="CONFIRMADO"
    )

    db.add(nuevo_movimiento)
    await db.commit()
    await db.refresh(nuevo_movimiento)

    logger.info(f"Movimiento {nuevo_movimiento.id_movimiento} registrado con éxito por '{current_user.username}'")
    return nuevo_movimiento


@router.post("/storno", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def storno_movement(
        storno_in: StornoRequest,
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. Validación de Firma Electrónica
    if not verify_password(storno_in.signature_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma rechazada: Contraseña incorrecta"
        )

    if not verify_totp_code(current_user.mfa_secret, storno_in.signature_totp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma rechazada: Código MFA inválido"
        )

    # 2. Recuperar el movimiento original a anular
    query_orig = select(LibroEstupefacientes).where(
        LibroEstupefacientes.id_movimiento == storno_in.id_movimiento_original
    )
    res_orig = await db.execute(query_orig)
    mov_original = res_orig.scalar_one_or_none()

    if not mov_original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el movimiento con ID {storno_in.id_movimiento_original}"
        )

    if mov_original.tipo_movimiento == TipoMovimientoEnum.AJUSTE_STORNO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede aplicar un Storno sobre otro movimiento de Storno"
        )

    # 3. Obtener el saldo actual del producto
    query_last = (
        select(LibroEstupefacientes)
        .where(LibroEstupefacientes.id_producto == mov_original.id_producto)
        .order_by(LibroEstupefacientes.id_movimiento.desc())
        .limit(1)
    )
    result_last = await db.execute(query_last)
    ultimo_registro = result_last.scalar_one_or_none()

    saldo_actual = ultimo_registro.saldo_resultante if ultimo_registro else 0

    # 4. Calcular el saldo compensatorio
    if mov_original.tipo_movimiento == TipoMovimientoEnum.SALIDA.value:
        saldo_nuevo = saldo_actual + mov_original.cantidad
    elif mov_original.tipo_movimiento == TipoMovimientoEnum.ENTRADA.value:
        if saldo_actual < mov_original.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No es posible anular la ENTRADA: Saldo actual ({saldo_actual}) menor que la cantidad a retirar ({mov_original.cantidad})"
            )
        saldo_nuevo = saldo_actual - mov_original.cantidad
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de movimiento '{mov_original.tipo_movimiento}' no admite Storno directo"
        )

    # 5. Crear el asiento de Storno inmutable
    mov_storno = LibroEstupefacientes(
        id_producto=mov_original.id_producto,
        tipo_movimiento=TipoMovimientoEnum.AJUSTE_STORNO.value,
        num_lote=mov_original.num_lote,
        fecha_caducidad=mov_original.fecha_caducidad,
        cantidad=mov_original.cantidad,
        saldo_resultante=saldo_nuevo,
        doc_referencia=f"STORNO-REF-{mov_original.id_movimiento}",
        prescriptor_destino=f"ANULACION REGISTRO ID #{mov_original.id_movimiento}",
        motivo_ajuste=storno_in.motivo_ajuste,
        id_usuario_firma=current_user.id_usuario,
        estado="CONFIRMADO"
    )

    db.add(mov_storno)
    await db.commit()
    await db.refresh(mov_storno)

    logger.info(
        f"Storno registrado con éxito: Movimiento {mov_storno.id_movimiento} anula Movimiento {mov_original.id_movimiento}")
    return mov_storno


@router.get("/book/{id_producto}", response_model=List[LedgerEntryResponse])
async def get_official_ledger(
        id_producto: int,
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = (
        select(LibroEstupefacientes)
        .where(LibroEstupefacientes.id_producto == id_producto)
        .order_by(LibroEstupefacientes.id_movimiento.asc())
    )
    result = await db.execute(query)
    entries = result.scalars().all()
    return entries


@router.get("/audit-trail", response_model=List[AuditTrailResponse])
async def get_audit_trail(
        limit: int = 50,
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = select(AuditTrail).order_by(AuditTrail.id_audit.desc()).limit(limit)
    result = await db.execute(query)
    trails = result.scalars().all()
    return trails


@router.get("/export/csv/{id_producto}")
async def export_ledger_csv(
        id_producto: int,
        current_user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = (
        select(LibroEstupefacientes)
        .where(LibroEstupefacientes.id_producto == id_producto)
        .order_by(LibroEstupefacientes.id_movimiento.asc())
    )
    result = await db.execute(query)
    records = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        "ID_ASIENTO", "FECHA_HORA_NTP", "TIPO_MOVIMIENTO", "LOTE",
        "CADUCIDAD", "CANTIDAD", "SALDO", "DOC_REFERENCIA",
        "DESTINO_PRESCRIPTOR", "MOTIVO_AJUSTE", "ESTADO"
    ])

    for r in records:
        writer.writerow([
            r.id_movimiento,
            r.timestamp_servidor.isoformat(),
            r.tipo_movimiento,
            r.num_lote,
            r.fecha_caducidad.isoformat(),
            r.cantidad,
            r.saldo_resultante,
            r.doc_referencia,
            r.prescriptor_destino or "",
            r.motivo_ajuste or "",
            r.estado
        ])

    output.seek(0)
    filename = f"Libro_Oficial_Estupefacientes_Prod_{id_producto}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )