from datetime import datetime, timedelta
from http import HTTPStatus

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from jwt import (
    encode,
)
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app.database import get_session
from app.models import User
from app.settings import Settings

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
n8n_security = HTTPBearer()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    # Adiciona um tempo para expiração
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES
    )

    to_encode.update({'exp': expire})

    encoded_jwt = encode(
        to_encode, Settings().JWT_SECRET, algorithm=Settings().JWT_ALGORITHM
    )

    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, Settings().JWT_SECRET, algorithms=Settings().JWT_ALGORITHM
        )
        id = payload.get('sub')

        if not id:
            raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user_db = session.scalar(select(User).where(User.id == id))

    if not user_db:
        raise credentials_exception

    return user_db


def verify_n8n_token(
    credentials: HTTPAuthorizationCredentials = Depends(n8n_security),
):
    """Verifica se o token bearer é válido para o N8N."""
    settings = Settings()
    
    if not settings.N8N_BEARER_TOKEN:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='N8N_BEARER_TOKEN não configurado',
        )
    
    if credentials.credentials != settings.N8N_BEARER_TOKEN:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token inválido',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    return credentials.credentials
