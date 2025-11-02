from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_session
from app.models import PontoColeta, Empresa
from app.schemas import (
    PontoColetaCreate,
    PontoColetaUpdate,
    PontoColetaResponse
)
from app.geocoding_service import GeocodingService

router = APIRouter(
    prefix='/pontos-coleta',
    tags=['pontos-coleta']
)

T_Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=PontoColetaResponse
)
async def criar_ponto_coleta(
    ponto_data: PontoColetaCreate,
    session: T_Session
):
    """
    Cria um novo ponto de coleta.
    """
    # Verifica se a empresa existe
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == ponto_data.empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    # Geocodifica o endereço
    coordenadas = await GeocodingService.geocode_address(
        ponto_data.endereco
    )
    
    latitude = None
    longitude = None
    if coordenadas:
        latitude = coordenadas.get("latitude")
        longitude = coordenadas.get("longitude")

    novo_ponto = PontoColeta(
        empresa_id=ponto_data.empresa_id,
        nome=ponto_data.nome,
        endereco=ponto_data.endereco,
        horario_funcionamento=ponto_data.horario_funcionamento,
        telefone=ponto_data.telefone,
        status=ponto_data.status,
        latitude=latitude,
        longitude=longitude,
    )

    session.add(novo_ponto)
    session.commit()
    session.refresh(novo_ponto)

    return novo_ponto


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=List[PontoColetaResponse]
)
def listar_pontos_coleta(session: T_Session):
    """
    Lista todos os pontos de coleta.
    """
    pontos = session.scalars(select(PontoColeta)).all()
    return pontos


@router.get(
    '/{ponto_id}',
    status_code=HTTPStatus.OK,
    response_model=PontoColetaResponse
)
def obter_ponto_coleta(ponto_id: int, session: T_Session):
    """
    Obtém um ponto de coleta pelo ID.
    """
    ponto = session.scalar(
        select(PontoColeta).where(PontoColeta.id == ponto_id)
    )

    if not ponto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ponto de coleta não encontrado'
        )

    return ponto


@router.get(
    '/empresa/{empresa_id}',
    status_code=HTTPStatus.OK,
    response_model=List[PontoColetaResponse]
)
def listar_pontos_por_empresa(
    empresa_id: int,
    session: T_Session
):
    """
    Lista todos os pontos de coleta de uma empresa.
    """
    # Verifica se a empresa existe
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    pontos = session.scalars(
        select(PontoColeta).where(
            PontoColeta.empresa_id == empresa_id
        )
    ).all()

    return pontos


@router.put(
    '/{ponto_id}',
    status_code=HTTPStatus.OK,
    response_model=PontoColetaResponse
)
async def atualizar_ponto_coleta(
    ponto_id: int,
    ponto_data: PontoColetaUpdate,
    session: T_Session
):
    """
    Atualiza um ponto de coleta existente.
    """
    ponto = session.scalar(
        select(PontoColeta).where(PontoColeta.id == ponto_id)
    )

    if not ponto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ponto de coleta não encontrado'
        )

    # Atualiza apenas os campos fornecidos
    update_data = ponto_data.dict(exclude_unset=True)

    # Se o endereço foi alterado, geocodificar novamente
    if 'endereco' in update_data:
        coordenadas = await GeocodingService.geocode_address(
            update_data['endereco']
        )
        if coordenadas:
            update_data['latitude'] = coordenadas.get("latitude")
            update_data['longitude'] = coordenadas.get("longitude")

    for campo, valor in update_data.items():
        setattr(ponto, campo, valor)

    session.commit()
    session.refresh(ponto)

    return ponto


@router.delete(
    '/{ponto_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def deletar_ponto_coleta(ponto_id: int, session: T_Session):
    """
    Deleta um ponto de coleta pelo ID.
    """
    ponto = session.scalar(
        select(PontoColeta).where(PontoColeta.id == ponto_id)
    )

    if not ponto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ponto de coleta não encontrado'
        )

    session.delete(ponto)
    session.commit()

    return None
