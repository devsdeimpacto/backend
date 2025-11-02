from http import HTTPStatus
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_session
from app.models import SolicitacaoColeta, OrdemServico, StatusOS
from app.schemas import (
    SolicitacaoColetaCreate,
    SolicitacaoColetaResponse
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

