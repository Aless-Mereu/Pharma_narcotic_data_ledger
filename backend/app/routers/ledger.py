from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, verify_totp_code
from backend.app.models.domain import Usuario, LibroEstupefacientes, ProductoEstupefaciente
from backend.app.schemas.ledger import MovementCreate, MovementResponse
from backend.app.routers.auth import get_current_user

# Contiene el cálculo dinámico y atómico de saldo, la re-autenticación de firma y la inserción transaccional
router = APIRouter(prefix="/ledger", tags=["Libro Diligenciado GxP"])

@router.post("/movement", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def register_movement(
    payload: MovementCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verificación de permisos de rol GxP
    if current_user.rol not in ["FARMACEUTICO", "DIRECTOR_TECNICO"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol insuficiente para firmar movimientos de estupefacientes"
        )

    # 2. Re-Autenticación (Firma Electrónica en el momento del registro)
    if not verify_password(payload.signature_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firma rechazada: Contraseña incorrecta")
    if not verify_totp_code(current_user.mfa_secret, payload.signature_totp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firma rechazada: Código MFA inválido")

    # 3. Comprobar que el producto existe
    prod_query = select(ProductoEstupefaciente).where(ProductoEstupefaciente.id_producto == payload.id_producto)
    prod_res = await db.execute(prod_query)
    if not prod_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto estupefaciente no encontrado")

    # 4. Obtener último saldo registrado para ese producto
    last_mov_query = (
        select(LibroEstupefacientes)
        .where(LibroEstupefacientes.id_producto == payload.id_producto)
        .order_by(desc(LibroEstupefacientes.id_movimiento))
        .limit(1)
    )
    last_mov_res = await db.execute(last_mov_query)
    last_mov = last_mov_res.scalar_one_or_none()
    saldo_anterior = last_mov.saldo_resultante if last_mov else 0

    # 5. Cálculo Dinámico de Saldo
    if payload.tipo_movimiento == "ENTRADA":
        nuevo_saldo = saldo_anterior + payload.cantidad
    elif payload.tipo_movimiento in ["SALIDA", "AJUSTE_MERMA", "STORNO"]:
        if saldo_anterior < payload.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo actual: {saldo_anterior}, intentado retirar: {payload.cantidad}"
            )
        nuevo_saldo = saldo_anterior - payload.cantidad
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de movimiento no válido")

    # 6. Inserción Transaccional (disparará el trigger de audit_trail en PostgreSQL)
    nuevo_movimiento = LibroEstupefacientes(
        id_producto=payload.id_producto,
        tipo_movimiento=payload.tipo_movimiento,
        num_lote=payload.num_lote,
        fecha_caducidad=payload.fecha_caducidad,
        cantidad=payload.cantidad,
        saldo_resultante=nuevo_saldo,
        doc_referencia=payload.doc_referencia,
        prescriptor_destino=payload.prescriptor_destino,
        motivo_ajuste=payload.motivo_ajuste,
        id_usuario_firma=current_user.id_usuario,
        estado="CONFIRMADO"
    )

    db.add(nuevo_movimiento)
    await db.commit()
    await db.refresh(nuevo_movimiento)

    return nuevo_movimiento