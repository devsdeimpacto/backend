from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Table,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class TipoPessoa(str, enum.Enum):
    PF = "PF"
    PJ = "PJ"


class StatusOS(str, enum.Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class StatusEmpresa(str, enum.Enum):
    ATIVA = "ATIVA"
    INATIVA = "INATIVA"


class StatusPontoColeta(str, enum.Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"


class StatusCatador(str, enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"


# Tabela associativa para relacionamento muitos-para-muitos
catadores_empresas = Table(
    'catadores_empresas',
    Base.metadata,
    Column(
        'catador_id',
        Integer,
        ForeignKey('catadores.id'),
        primary_key=True
    ),
    Column(
        'empresa_id',
        Integer,
        ForeignKey('empresas.id'),
        primary_key=True
    ),
    Column(
        'data_vinculo',
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
)


class SolicitacaoColeta(Base):
    __tablename__ = "solicitacoes_coleta"

    id = Column(Integer, primary_key=True, index=True)
    nome_solicitante = Column(String(255), nullable=False)
    tipo_pessoa = Column(SQLEnum(TipoPessoa), nullable=False)
    documento = Column(String(18), nullable=False)
    email = Column(String(255), nullable=False)
    whatsapp = Column(String(20), nullable=False)
    quantidade_itens = Column(Integer, nullable=False)
    endereco = Column(String(500), nullable=False)
    foto_url = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento
    ordem_servico = relationship(
        "OrdemServico",
        back_populates="solicitacao",
        uselist=False
    )

    def __repr__(self):
        return (
            f"<SolicitacaoColeta(id={self.id}, "
            f"nome={self.nome_solicitante}, "
            f"tipo_pessoa={self.tipo_pessoa})>"
        )


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    solicitacao_id = Column(
        Integer,
        ForeignKey("solicitacoes_coleta.id"),
        nullable=False,
        unique=True
    )
    numero_os = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(StatusOS),
        default=StatusOS.PENDENTE,
        nullable=False
    )
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=True
    )
    ponto_coleta_id = Column(
        Integer,
        ForeignKey("pontos_coleta.id"),
        nullable=True
    )
    catador_id = Column(
        Integer,
        ForeignKey("catadores.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    solicitacao = relationship(
        "SolicitacaoColeta",
        back_populates="ordem_servico"
    )
    empresa = relationship("Empresa")
    ponto_coleta = relationship("PontoColeta")
    catador = relationship("Catador")

    def __repr__(self):
        return (
            f"<OrdemServico(id={self.id}, numero_os={self.numero_os}, "
            f"status={self.status})>"
        )


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=False, unique=True)
    endereco = Column(String(500), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    status = Column(
        SQLEnum(StatusEmpresa),
        default=StatusEmpresa.ATIVA,
        nullable=False
    )
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    pontos_coleta = relationship(
        "PontoColeta",
        back_populates="empresa"
    )
    catadores = relationship(
        "Catador",
        secondary=catadores_empresas,
        back_populates="empresas"
    )

    def __repr__(self):
        return f"<Empresa(id={self.id}, nome={self.nome})>"


class PontoColeta(Base):
    __tablename__ = "pontos_coleta"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id"),
        nullable=False
    )
    nome = Column(String(255), nullable=False)
    endereco = Column(String(500), nullable=False)
    horario_funcionamento = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False)
    status = Column(
        SQLEnum(StatusPontoColeta),
        default=StatusPontoColeta.ABERTO,
        nullable=False
    )
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento
    empresa = relationship("Empresa", back_populates="pontos_coleta")

    def __repr__(self):
        return f"<PontoColeta(id={self.id}, nome={self.nome})>"


class Catador(Base):
    __tablename__ = "catadores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    status = Column(
        SQLEnum(StatusCatador),
        default=StatusCatador.ATIVO,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento muitos-para-muitos
    empresas = relationship(
        "Empresa",
        secondary=catadores_empresas,
        back_populates="catadores"
    )

    def __repr__(self):
        return f"<Catador(id={self.id}, nome={self.nome})>"
