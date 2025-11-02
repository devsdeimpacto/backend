from http import HTTPStatus
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_session
from app.models import SolicitacaoColeta, OrdemServico, StatusOS
from app.schemas import (
    SolicitacaoColetaCreate,
    SolicitacaoColetaResponse,
    SolicitacaoColetaUpdate,
    SolicitacaoColetaList,
    OrdemServicoUpdateStatus,
    OrdemServicoResponse,
    OrdemServicoList
)

router = APIRouter(prefix='/solicitacoes', tags=['solicitacoes'])

T_Session = Annotated[Session, Depends(get_session)]


def gerar_numero_os(session: Session) -> str:
    """
    Gera um número único de OS no formato OS-YYYY-NNNNN
    Ex: OS-2025-00001
    """
    ano_atual = datetime.now().year

    # Busca o último número da OS do ano atual
    ultima_os = session.scalar(
        select(OrdemServico)
        .where(
            OrdemServico.numero_os.like(f'OS-{ano_atual}-%')
        )
        .order_by(OrdemServico.id.desc())
    )

    if ultima_os:
        # Extrai o número sequencial da última OS
        ultimo_numero = int(ultima_os.numero_os.split('-')[-1])
        proximo_numero = ultimo_numero + 1
    else:
        # Primeira OS do ano
        proximo_numero = 1

    # Formata com 5 dígitos
    numero_os = f'OS-{ano_atual}-{proximo_numero:05d}'

    return numero_os


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=SolicitacaoColetaResponse
)
def criar_solicitacao_coleta(
    solicitacao_data: SolicitacaoColetaCreate,
    session: T_Session
):
    """
    Cria uma nova solicitação de coleta e
    automaticamente gera uma ordem de serviço associada.
    """
    # Cria a solicitação
    nova_solicitacao = SolicitacaoColeta(
        nome_solicitante=solicitacao_data.nome_solicitante,
        tipo_pessoa=solicitacao_data.tipo_pessoa,
        documento=solicitacao_data.documento,
        email=solicitacao_data.email,
        whatsapp=solicitacao_data.whatsapp,
        quantidade_itens=solicitacao_data.quantidade_itens,
        endereco=solicitacao_data.endereco,
        foto_url=solicitacao_data.foto_url,
    )

    session.add(nova_solicitacao)
    session.flush()  # Garante que o ID da solicitação seja gerado

    # Gera o número da OS
    numero_os = gerar_numero_os(session)

    # Cria a ordem de serviço
    nova_ordem = OrdemServico(
        solicitacao_id=nova_solicitacao.id,
        numero_os=numero_os,
        status=StatusOS.PENDENTE
    )

    session.add(nova_ordem)
    session.commit()
    session.refresh(nova_solicitacao)
    session.refresh(nova_ordem)

    # Monta o response com os dados da solicitação e ordem
    response_data = {
        "id": nova_solicitacao.id,
        "nome_solicitante": nova_solicitacao.nome_solicitante,
        "tipo_pessoa": nova_solicitacao.tipo_pessoa,
        "documento": nova_solicitacao.documento,
        "email": nova_solicitacao.email,
        "whatsapp": nova_solicitacao.whatsapp,
        "quantidade_itens": nova_solicitacao.quantidade_itens,
        "endereco": nova_solicitacao.endereco,
        "foto_url": nova_solicitacao.foto_url,
        "created_at": nova_solicitacao.created_at,
        "ordem_servico_id": nova_ordem.id,
        "numero_os": nova_ordem.numero_os,
    }

    return response_data


@router.get(
    '/',
    response_model=SolicitacaoColetaList
)
def listar_solicitacoes(
    session: T_Session,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    tipo_pessoa: Optional[str] = Query(None, description="Filtrar por tipo de pessoa (PF/PJ)"),
    documento: Optional[str] = Query(None, description="Filtrar por documento"),
):
    """
    Lista todas as solicitações de coleta com paginação e filtros opcionais.
    """
    # Query base
    query = select(SolicitacaoColeta).join(OrdemServico)
    
    # Aplicar filtros se fornecidos
    if tipo_pessoa:
        query = query.where(SolicitacaoColeta.tipo_pessoa == tipo_pessoa)
    
    if documento:
        query = query.where(SolicitacaoColeta.documento == documento)
    
    # Contar total de registros
    count_query = select(func.count()).select_from(query.subquery())
    total = session.scalar(count_query)
    
    # Aplicar paginação e ordenação
    query = query.order_by(SolicitacaoColeta.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    # Executar query
    solicitacoes = session.scalars(query).all()
    
    # Montar response
    items = []
    for solicitacao in solicitacoes:
        items.append({
            "id": solicitacao.id,
            "nome_solicitante": solicitacao.nome_solicitante,
            "tipo_pessoa": solicitacao.tipo_pessoa,
            "documento": solicitacao.documento,
            "email": solicitacao.email,
            "whatsapp": solicitacao.whatsapp,
            "quantidade_itens": solicitacao.quantidade_itens,
            "endereco": solicitacao.endereco,
            "foto_url": solicitacao.foto_url,
            "created_at": solicitacao.created_at,
            "ordem_servico_id": solicitacao.ordem_servico.id,
            "numero_os": solicitacao.ordem_servico.numero_os,
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }


@router.get(
    '/{solicitacao_id}',
    response_model=SolicitacaoColetaResponse
)
def obter_solicitacao(
    solicitacao_id: int,
    session: T_Session
):
    """
    Obtém os detalhes de uma solicitação de coleta específica.
    """
    solicitacao = session.scalar(
        select(SolicitacaoColeta)
        .where(SolicitacaoColeta.id == solicitacao_id)
    )
    
    if not solicitacao:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Solicitação de coleta não encontrada'
        )
    
    return {
        "id": solicitacao.id,
        "nome_solicitante": solicitacao.nome_solicitante,
        "tipo_pessoa": solicitacao.tipo_pessoa,
        "documento": solicitacao.documento,
        "email": solicitacao.email,
        "whatsapp": solicitacao.whatsapp,
        "quantidade_itens": solicitacao.quantidade_itens,
        "endereco": solicitacao.endereco,
        "foto_url": solicitacao.foto_url,
        "created_at": solicitacao.created_at,
        "ordem_servico_id": solicitacao.ordem_servico.id,
        "numero_os": solicitacao.ordem_servico.numero_os,
    }


@router.patch(
    '/{solicitacao_id}',
    response_model=SolicitacaoColetaResponse
)
def atualizar_solicitacao(
    solicitacao_id: int,
    solicitacao_data: SolicitacaoColetaUpdate,
    session: T_Session
):
    """
    Atualiza parcialmente os dados de uma solicitação de coleta.
    Não é possível alterar o documento ou tipo de pessoa.
    """
    solicitacao = session.scalar(
        select(SolicitacaoColeta)
        .where(SolicitacaoColeta.id == solicitacao_id)
    )
    
    if not solicitacao:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Solicitação de coleta não encontrada'
        )
    
    # Atualizar apenas os campos fornecidos
    update_data = solicitacao_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(solicitacao, field, value)
    
    session.commit()
    session.refresh(solicitacao)
    
    return {
        "id": solicitacao.id,
        "nome_solicitante": solicitacao.nome_solicitante,
        "tipo_pessoa": solicitacao.tipo_pessoa,
        "documento": solicitacao.documento,
        "email": solicitacao.email,
        "whatsapp": solicitacao.whatsapp,
        "quantidade_itens": solicitacao.quantidade_itens,
        "endereco": solicitacao.endereco,
        "foto_url": solicitacao.foto_url,
        "created_at": solicitacao.created_at,
        "ordem_servico_id": solicitacao.ordem_servico.id,
        "numero_os": solicitacao.ordem_servico.numero_os,
    }


@router.get(
    '/ordens-servico',
    response_model=OrdemServicoList
)
def listar_ordens_servico(
    session: T_Session,
    skip: int = Query(
        0, ge=0,
        description="Número de registros para pular"
    ),
    limit: int = Query(
        100, ge=1, le=100,
        description="Limite de registros por página"
    ),
    status: Optional[str] = Query(
        None,
        description="Filtrar por status"
    ),
):
    """
    Lista todas as ordens de serviço com paginação
    e filtros opcionais.
    Endpoint útil para o coletor visualizar as ordens.
    """
    # Query base
    query = select(OrdemServico)

    # Aplicar filtro de status se fornecido
    if status:
        query = query.where(OrdemServico.status == status)

    # Contar total de registros
    count_query = select(func.count()).select_from(query.subquery())
    total = session.scalar(count_query)

    # Aplicar paginação e ordenação
    query = query.order_by(OrdemServico.created_at.desc())
    query = query.offset(skip).limit(limit)

    # Executar query
    ordens = session.scalars(query).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": ordens
    }


@router.get(
    '/ordens-servico/{ordem_servico_id}',
    response_model=OrdemServicoResponse
)
def obter_ordem_servico(
    ordem_servico_id: int,
    session: T_Session
):
    """
    Obtém os detalhes de uma ordem de serviço específica.
    """
    ordem_servico = session.scalar(
        select(OrdemServico)
        .where(OrdemServico.id == ordem_servico_id)
    )

    if not ordem_servico:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ordem de serviço não encontrada'
        )

    return ordem_servico


@router.patch(
    '/ordens-servico/{ordem_servico_id}/status',
    response_model=OrdemServicoResponse
)
def atualizar_status_ordem_servico(
    ordem_servico_id: int,
    status_data: OrdemServicoUpdateStatus,
    session: T_Session
):
    """
    Atualiza o status de uma ordem de serviço.
    Endpoint para ser usado pelo coletor.
    """
    ordem_servico = session.scalar(
        select(OrdemServico)
        .where(OrdemServico.id == ordem_servico_id)
    )

    if not ordem_servico:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ordem de serviço não encontrada'
        )

    # Atualiza o status
    ordem_servico.status = status_data.status

    session.commit()
    session.refresh(ordem_servico)

    return ordem_servico