from http import HTTPStatus
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_session
from app.models import Catador, Empresa
from app.schemas import (
    CatadorCreate,
    CatadorUpdate,
    CatadorResponse,
    CatadorSimples,
    EmpresaSimples,
    StatusCatadorEnum
)

router = APIRouter(prefix='/catadores', tags=['catadores'])

T_Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=CatadorResponse
)
def criar_catador(
    catador_data: CatadorCreate,
    session: T_Session
):
    """
    Cria um novo catador.
    """
    # Verificar se CPF já existe
    catador_existente = session.scalar(
        select(Catador).where(Catador.cpf == catador_data.cpf)
    )

    if catador_existente:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='CPF já cadastrado'
        )

    # Criar catador
    catador_dict = catador_data.dict(exclude={'empresas_ids'})
    novo_catador = Catador(**catador_dict)

    # Vincular empresas se foram fornecidas
    if catador_data.empresas_ids:
        empresas = session.scalars(
            select(Empresa).where(
                Empresa.id.in_(catador_data.empresas_ids)
            )
        ).all()

        if len(empresas) != len(catador_data.empresas_ids):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Uma ou mais empresas não encontradas'
            )

        novo_catador.empresas = list(empresas)

    session.add(novo_catador)
    session.commit()
    session.refresh(novo_catador)

    return novo_catador


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=List[CatadorResponse]
)
def listar_catadores(
    session: T_Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusCatadorEnum] = None,
    empresa_id: Optional[int] = None
):
    """
    Lista catadores com filtros opcionais.
    """
    query = select(Catador)

    if status:
        query = query.where(Catador.status == status)

    if empresa_id:
        # Filtrar catadores que trabalham em uma empresa específica
        query = query.join(Catador.empresas).where(
            Empresa.id == empresa_id
        )

    catadores = session.scalars(
        query.offset(skip).limit(limit)
    ).all()

    return list(catadores)


@router.get(
    '/{catador_id}',
    status_code=HTTPStatus.OK,
    response_model=CatadorResponse
)
def obter_catador(catador_id: int, session: T_Session):
    """
    Obtém um catador pelo ID.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    return catador


@router.put(
    '/{catador_id}',
    status_code=HTTPStatus.OK,
    response_model=CatadorResponse
)
def atualizar_catador(
    catador_id: int,
    catador_data: CatadorUpdate,
    session: T_Session
):
    """
    Atualiza um catador existente.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    # Atualizar campos
    update_data = catador_data.dict(
        exclude_unset=True,
        exclude={'empresas_ids'}
    )

    for campo, valor in update_data.items():
        setattr(catador, campo, valor)

    # Atualizar empresas se fornecido
    if catador_data.empresas_ids is not None:
        empresas = session.scalars(
            select(Empresa).where(
                Empresa.id.in_(catador_data.empresas_ids)
            )
        ).all()

        if len(empresas) != len(catador_data.empresas_ids):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Uma ou mais empresas não encontradas'
            )

        catador.empresas = list(empresas)

    session.commit()
    session.refresh(catador)

    return catador


@router.delete(
    '/{catador_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def deletar_catador(catador_id: int, session: T_Session):
    """
    Deleta um catador pelo ID.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    session.delete(catador)
    session.commit()

    return None


# Endpoints para gerenciar o vínculo entre catador e empresa
@router.post(
    '/{catador_id}/empresas/{empresa_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def vincular_empresa(
    catador_id: int,
    empresa_id: int,
    session: T_Session
):
    """
    Vincula um catador a uma empresa.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    if empresa in catador.empresas:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Catador já vinculado a esta empresa'
        )

    catador.empresas.append(empresa)
    session.commit()

    return None


@router.delete(
    '/{catador_id}/empresas/{empresa_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def desvincular_empresa(
    catador_id: int,
    empresa_id: int,
    session: T_Session
):
    """
    Desvincula um catador de uma empresa.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    empresa = session.scalar(
        select(Empresa).where(Empresa.id == empresa_id)
    )

    if not empresa:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Empresa não encontrada'
        )

    if empresa not in catador.empresas:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Catador não está vinculado a esta empresa'
        )

    catador.empresas.remove(empresa)
    session.commit()

    return None


@router.get(
    '/{catador_id}/empresas',
    status_code=HTTPStatus.OK,
    response_model=List[EmpresaSimples]
)
def listar_empresas_catador(
    catador_id: int,
    session: T_Session
):
    """
    Lista as empresas vinculadas a um catador.
    """
    catador = session.scalar(
        select(Catador).where(Catador.id == catador_id)
    )

    if not catador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Catador não encontrado'
        )

    return catador.empresas

