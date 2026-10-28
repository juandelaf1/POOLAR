import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = os.getenv("TRAMA_ABIERTA_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("TRAMA_ABIERTA_SECRET_KEY no configurada; no iniciar sin secreto aleatorio de entorno")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# PBKDF2-SHA256 evita dependencias binarias frágiles (bcrypt/passlib) y
# mantiene un coste configurable. No se usa ninguna contraseña por defecto.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=260000,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    organizacion_id: Optional[int] = None
    user_id: Optional[int] = None

class UserInDB(BaseModel):
    id: int
    organizacion_id: int
    email: str
    hashed_password: str
    rol: str = "miembro"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Auth independiente (individuo) o organizacional (operación).
# Si el token no tiene `organizacion_id` o `persona_id`, se rechaza.
# Nunca ambas al mismo tiempo.


def get_current_user_org(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    org_id = payload.get("organizacion_id")
    persona_id = payload.get("persona_id")
    if org_id is not None and persona_id is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ambiguo: contexto organizativo e individual simultáneo",
        )
    if org_id is not None:
        return {
            "tipo": "organizacion",
            "organizacion_id": org_id,
            "user_id": payload.get("user_id"),
            "rol": payload.get("rol", "miembro"),
            "persona_id": None,
        }
    if persona_id is not None:
        return {
            "tipo": "individuo",
            "organizacion_id": None,
            "user_id": payload.get("user_id"),
            "rol": payload.get("rol", "individuo"),
            "persona_id": persona_id,
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token sin contexto: falta organizacion_id o persona_id",
        headers={"WWW-Authenticate": "Bearer"},
    )
