from http import HTTPStatus
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from app.database import get_session
from app.models import (
    SolicitacaoColeta,
    OrdemServico,
    StatusOS,
    Empresa,
    PontoColeta,
    Catador
)
from app.schemas import (
    SolicitacaoColetaCreate,
    SolicitacaoColetaResponse,
    SolicitacaoColetaUpdate,
    SolicitacaoColetaList,
    OrdemServicoUpdateStatus,
    OrdemServicoResponse,
    OrdemServicoList,
    OrdemServicoAtribuir
)
from app.geocoding_service import GeocodingService

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
async def criar_solicitacao_coleta(
    solicitacao_data: SolicitacaoColetaCreate,
    session: T_Session
):
    """
    Cria uma nova solicitação de coleta e
    automaticamente gera uma ordem de serviço associada.
    """
    # Geocodifica o endereço
    coordenadas = await GeocodingService.geocode_address(
        solicitacao_data.endereco
    )
    
    latitude = None
    longitude = None
    if coordenadas:
        latitude = coordenadas.get("latitude")
        longitude = coordenadas.get("longitude")
    
    # Cria a solicitação
    nova_solicitacao = SolicitacaoColeta(
        nome_solicitante=solicitacao_data.nome_solicitante,
        tipo_pessoa=solicitacao_data.tipo_pessoa,
        documento=solicitacao_data.documento,
        email=solicitacao_data.email,
        whatsapp=solicitacao_data.whatsapp,
        quantidade_itens=solicitacao_data.quantidade_itens,
        tipo_material=solicitacao_data.tipo_material,
        endereco=solicitacao_data.endereco,
        foto_url=solicitacao_data.foto_url,
        latitude=latitude,
        longitude=longitude,
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
        "tipo_material": nova_solicitacao.tipo_material,
        "endereco": nova_solicitacao.endereco,
        "foto_url": nova_solicitacao.foto_url,
        "latitude": nova_solicitacao.latitude,
        "longitude": nova_solicitacao.longitude,
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
    
    # Montar response usando o schema Pydantic
    items = []
    for solicitacao in solicitacoes:
        item = SolicitacaoColetaResponse(
            id=solicitacao.id,
            nome_solicitante=solicitacao.nome_solicitante,
            tipo_pessoa=solicitacao.tipo_pessoa,
            documento=solicitacao.documento,
            email=solicitacao.email,
            whatsapp=solicitacao.whatsapp,
            quantidade_itens=solicitacao.quantidade_itens,
            tipo_material=solicitacao.tipo_material,
            endereco=solicitacao.endereco,
            foto_url=solicitacao.foto_url,
            latitude=solicitacao.latitude,
            longitude=solicitacao.longitude,
            created_at=solicitacao.created_at,
            ordem_servico_id=solicitacao.ordem_servico.id,
            numero_os=solicitacao.ordem_servico.numero_os,
        )
        items.append(item)
    
    return SolicitacaoColetaList(
        total=total,
        skip=skip,
        limit=limit,
        items=items
    )


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
    Retorna dados completos incluindo solicitação, empresa,
    ponto de coleta e catador.
    """
    # Query base para contagem (sem joinedload)
    count_query = select(func.count()).select_from(OrdemServico)

    # Query base com joins para carregar todos os relacionamentos
    query = (
        select(OrdemServico)
        .options(
            joinedload(OrdemServico.solicitacao),
            joinedload(OrdemServico.empresa),
            joinedload(OrdemServico.ponto_coleta),
            joinedload(OrdemServico.catador)
        )
    )

    # Aplicar filtro de status se fornecido
    if status:
        count_query = count_query.where(OrdemServico.status == status)
        query = query.where(OrdemServico.status == status)

    # Contar total de registros
    total = session.scalar(count_query)

    # Aplicar paginação e ordenação
    query = query.order_by(OrdemServico.created_at.desc())
    query = query.offset(skip).limit(limit)

    # Executar query
    ordens = session.scalars(query).unique().all()

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
    Obtém os detalhes completos de uma ordem de serviço,
    incluindo solicitação, empresa, ponto de coleta e catador.
    """
    ordem_servico = session.scalar(
        select(OrdemServico)
        .options(
            joinedload(OrdemServico.solicitacao),
            joinedload(OrdemServico.empresa),
            joinedload(OrdemServico.ponto_coleta),
            joinedload(OrdemServico.catador)
        )
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
        .options(
            joinedload(OrdemServico.solicitacao),
            joinedload(OrdemServico.empresa),
            joinedload(OrdemServico.ponto_coleta),
            joinedload(OrdemServico.catador)
        )
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


@router.patch(
    '/ordens-servico/{ordem_servico_id}/atribuir',
    response_model=OrdemServicoResponse
)
def atribuir_ordem_servico(
    ordem_servico_id: int,
    atribuicao_data: OrdemServicoAtribuir,
    session: T_Session
):
    """
    Atribui empresa, ponto de coleta e/ou catador a uma OS.
    Útil para gerenciar a alocação de recursos para coleta.
    """
    # Busca a ordem de serviço
    ordem_servico = session.scalar(
        select(OrdemServico)
        .where(OrdemServico.id == ordem_servico_id)
    )

    if not ordem_servico:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ordem de serviço não encontrada'
        )

    # Valida e atribui empresa se fornecida
    if atribuicao_data.empresa_id is not None:
        empresa = session.scalar(
            select(Empresa)
            .where(Empresa.id == atribuicao_data.empresa_id)
        )
        if not empresa:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Empresa não encontrada'
            )
        ordem_servico.empresa_id = atribuicao_data.empresa_id

    # Valida e atribui ponto de coleta se fornecido
    if atribuicao_data.ponto_coleta_id is not None:
        ponto_coleta = session.scalar(
            select(PontoColeta)
            .where(PontoColeta.id == atribuicao_data.ponto_coleta_id)
        )
        if not ponto_coleta:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Ponto de coleta não encontrado'
            )
        ordem_servico.ponto_coleta_id = (
            atribuicao_data.ponto_coleta_id
        )

    # Valida e atribui catador se fornecido
    if atribuicao_data.catador_id is not None:
        catador = session.scalar(
            select(Catador)
            .where(Catador.id == atribuicao_data.catador_id)
        )
        if not catador:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Catador não encontrado'
            )
        ordem_servico.catador_id = atribuicao_data.catador_id

    session.commit()
    
    # Recarrega com todos os relacionamentos
    ordem_servico = session.scalar(
        select(OrdemServico)
        .options(
            joinedload(OrdemServico.solicitacao),
            joinedload(OrdemServico.empresa),
            joinedload(OrdemServico.ponto_coleta),
            joinedload(OrdemServico.catador)
        )
        .where(OrdemServico.id == ordem_servico_id)
    )

    return ordem_servico


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
        "tipo_material": solicitacao.tipo_material,
        "endereco": solicitacao.endereco,
        "foto_url": solicitacao.foto_url,
        "latitude": solicitacao.latitude,
        "longitude": solicitacao.longitude,
        "created_at": solicitacao.created_at,
        "ordem_servico_id": solicitacao.ordem_servico.id,
        "numero_os": solicitacao.ordem_servico.numero_os,
    }


@router.patch(
    '/{solicitacao_id}',
    response_model=SolicitacaoColetaResponse
)
async def atualizar_solicitacao(
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
    
    # Se o endereço foi alterado, geocodificar novamente
    if 'endereco' in update_data:
        coordenadas = await GeocodingService.geocode_address(
            update_data['endereco']
        )
        if coordenadas:
            update_data['latitude'] = coordenadas.get("latitude")
            update_data['longitude'] = coordenadas.get("longitude")
    
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
        "tipo_material": solicitacao.tipo_material,
        "endereco": solicitacao.endereco,
        "foto_url": solicitacao.foto_url,
        "latitude": solicitacao.latitude,
        "longitude": solicitacao.longitude,
        "created_at": solicitacao.created_at,
        "ordem_servico_id": solicitacao.ordem_servico.id,
        "numero_os": solicitacao.ordem_servico.numero_os,
    }


@router.delete(
    '/{solicitacao_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def deletar_solicitacao(
    solicitacao_id: int,
    session: T_Session
):
    """
    Deleta uma solicitação de coleta e sua ordem de
    serviço associada.
    
    IMPORTANTE: Este endpoint deleta:
    - A solicitação de coleta
    - A ordem de serviço associada (em cascata)
    
    NÃO deleta outras entidades como:
    - Empresa, Ponto de Coleta ou Catador
      (apenas remove as referências)
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
    
    session.delete(solicitacao)
    session.commit()
    
    return None


@router.delete(
    '/ordens-servico/{ordem_servico_id}',
    status_code=HTTPStatus.NO_CONTENT
)
def deletar_ordem_servico(
    ordem_servico_id: int,
    session: T_Session
):
    """
    Deleta apenas uma ordem de serviço específica.
    
    ATENÇÃO: A solicitação de coleta associada
    permanecerá no sistema.
    
    NÃO deleta outras entidades como:
    - Solicitação de Coleta
    - Empresa, Ponto de Coleta ou Catador
      (apenas remove as referências)
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
    
    session.delete(ordem_servico)
    session.commit()
    
    return None