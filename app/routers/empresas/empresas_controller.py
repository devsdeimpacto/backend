from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_session
from app.models import Empresa, Catador
from app.schemas import (
    EmpresaCreate,
    EmpresaUpdate,
    EmpresaResponse,
    CatadorSimples
)
from app.geocoding_service import GeocodingService

router = APIRouter(prefix='/empresas', tags=['empresas'])

T_Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=EmpresaResponse
)
async def criar_empresa(
    empresa_data: EmpresaCreate,
    session: T_Session
):
    """
    Cria uma nova empresa.
    """
    # Verifica se CNPJ já existe
    empresa_existente = session.scalar(
        select(Empresa).where(Empresa.cnpj == empresa_data.cnpj)
    )

    if empresa_existente:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='CNPJ já cadastrado'
        )

    # Geocodifica o endereço
    coordenadas = await GeocodingService.geocode_address(
        empresa_data.endereco
    )
    
    latitude = None
    longitude = None
    if coordenadas:
        latitude = coordenadas.get("latitude")
        longitude = coordenadas.get("longitude")

    nova_empresa = Empresa(
        nome=empresa_data.nome,
        cnpj=empresa_data.cnpj,
        endereco=empresa_data.endereco,
        telefone=empresa_data.telefone,
        email=empresa_data.email,
        status=empresa_data.status,
        latitude=latitude,
        longitude=longitude,
    )

    session.add(nova_empresa)
    session.commit()
    session.refresh(nova_empresa)

    return nova_empresa


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=List[EmpresaResponse]
)
def listar_empresas(session: T_Session):
    """
    Lista todas as empresas.
    """
    empresas = session.scalars(select(Empresa)).all()
    return empresas


@router.get(
    '/{empresa_id}',
    status_code=HTTPStatus.OK,
    response_model=EmpresaResponse
)
def obter_empresa(empresa_id: int, session: T_Session):
    """
    Obtém uma empresa pelo ID.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    return empresa


@router.put(
    '/{empresa_id}',
    status_code=HTTPStatus.OK,
    response_model=EmpresaResponse
)
async def atualizar_empresa(
    empresa_id: int,
    empresa_data: EmpresaUpdate,
    session: T_Session
):
    """
    Atualiza uma empresa existente.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    # Atualiza apenas os campos fornecidos
    update_data = empresa_data.dict(exclude_unset=True)

    # Se o endereço foi alterado, geocodificar novamente
    if 'endereco' in update_data:
        coordenadas = await GeocodingService.geocode_address(
            update_data['endereco']
        )
        if coordenadas:
            update_data['latitude'] = coordenadas.get("latitude")
            update_data['longitude'] = coordenadas.get("longitude")

    for campo, valor in update_data.items():
        setattr(empresa, campo, valor)

    session.commit()
    session.refresh(empresa)

    return empresa


@router.delete(
    '/{empresa_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def deletar_empresa(empresa_id: int, session: T_Session):
    """
    Deleta uma empresa pelo ID.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    session.delete(empresa)
    session.commit()

    return None


@router.get(
    '/{empresa_id}/catadores',
    status_code=HTTPStatus.OK,
    response_model=List[CatadorSimples]
)
def listar_catadores_empresa(
    empresa_id: int,
    session: T_Session
):
    """
    Lista os catadores vinculados a uma empresa.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    return empresa.catadores


@router.post(
    '/{empresa_id}/catadores/{catador_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def vincular_catador(
    empresa_id: int,
    catador_id: int,
    session: T_Session
):
    """
    Vincula um catador a uma empresa.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    if catador in empresa.catadores:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Catador já vinculado a esta empresa'
        )

    empresa.catadores.append(catador)
    session.commit()

    return None


@router.delete(
    '/{empresa_id}/catadores/{catador_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def desvincular_catador(
    empresa_id: int,
    catador_id: int,
    session: T_Session
):
    """
    Desvincula um catador de uma empresa.
    """
    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    if catador not in empresa.catadores:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Catador não está vinculado a esta empresa'
        )

    empresa.catadores.remove(catador)
    session.commit()

    return None
