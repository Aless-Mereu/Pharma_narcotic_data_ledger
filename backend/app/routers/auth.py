from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
import logging

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import verify_password, verify_totp_code, create_access_token
from backend.app.models.domain import Usuario
from backend.app.schemas.ledger import LoginRequest, Token, TokenData

logger = logging.getLogger("pharma_api")
router = APIRouter(prefix="/auth", tags=["Autenticación"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    query = select(Usuario).where(Usuario.username == credentials.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login fallido: Usuario '{credentials.username}' no encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    pwd_ok = verify_password(credentials.password, user.password_hash)
    if not pwd_ok:
        logger.warning(f"Login fallido: Contraseña no coincide para '{credentials.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (Password mismatch)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    totp_ok = verify_totp_code(user.mfa_secret, credentials.totp_code)
    if not totp_ok:
        logger.warning(f"Login fallido: TOTP inválido para '{credentials.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código MFA / TOTP inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username, "rol": user.rol, "id": user.id_usuario})
    logger.info(f"Login exitoso para '{user.username}' con rol '{user.rol}'")
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(Usuario).where(Usuario.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None or not user.activo:
        raise credentials_exception
    return user