from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from enum import Enum
import re
from datetime import datetime


class Message(BaseModel):
    message: str


class TipoPessoaEnum(str, Enum):
    PF = "PF"
    PJ = "PJ"


class StatusOSEnum(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class OrdemServicoUpdateStatus(BaseModel):
    status: StatusOSEnum

    class Config:
        json_schema_extra = {
            "example": {
                "status": "EM_ANDAMENTO"
            }
        }


class SolicitacaoColetaCreate(BaseModel):
    nome_solicitante: str = Field(..., min_length=3, max_length=255)
    tipo_pessoa: TipoPessoaEnum
    documento: str = Field(..., min_length=11, max_length=18)
    email: EmailStr
    whatsapp: str = Field(..., min_length=10, max_length=20)
    quantidade_itens: int = Field(..., gt=0)
    endereco: str = Field(..., min_length=10, max_length=500)
    foto_url: Optional[str] = Field(None, max_length=500)

    @validator('documento')
    def validate_documento(cls, v, values):
        apenas_numeros = re.sub(r'\D', '', v)

        if 'tipo_pessoa' in values:
            if (values['tipo_pessoa'] == TipoPessoaEnum.PF and
                    len(apenas_numeros) != 11):
                raise ValueError('CPF deve ter 11 dígitos')
            elif (values['tipo_pessoa'] == TipoPessoaEnum.PJ and
                  len(apenas_numeros) != 14):
                raise ValueError('CNPJ deve ter 14 dígitos')

        return v

    @validator('whatsapp')
    def validate_whatsapp(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
            raise ValueError(
                'WhatsApp deve ter entre 10 e 13 dígitos'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nome_solicitante": "João Silva",
                "tipo_pessoa": "PF",
                "documento": "123.456.789-00",
                "email": "cliente@exemplo.com",
                "whatsapp": "11987654321",
                "quantidade_itens": 5,
                "endereco": (
                    "Rua Exemplo, 123 - Bairro - "
                    "Cidade/UF - CEP"
                ),
                "foto_url": "https://storage.exemplo.com/fotos/12345.jpg"
            }
        }


class OrdemServicoResponse(BaseModel):
    id: int
    numero_os: str
    status: StatusOSEnum
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrdemServicoList(BaseModel):
    total: int
    skip: int
    limit: int
    items: List['OrdemServicoResponse']

    class Config:
        json_schema_extra = {
            "example": {
                "total": 25,
                "skip": 0,
                "limit": 10,
                "items": [
                    {
                        "id": 1,
                        "numero_os": "OS-2025-00001",
                        "status": "PENDENTE",
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "created_at": "2025-11-02T10:30:00Z",
                        "updated_at": None
                    }
                ]
            }
        }


class SolicitacaoColetaResponse(BaseModel):
    id: int
    nome_solicitante: str
    tipo_pessoa: TipoPessoaEnum
    documento: str
    email: str
    whatsapp: str
    quantidade_itens: int
    endereco: str
    foto_url: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    ordem_servico_id: int
    numero_os: str

    class Config:
        from_attributes = True


class StatusEmpresaEnum(str, Enum):
    ATIVA = "ATIVA"
    INATIVA = "INATIVA"


class StatusPontoColetaEnum(str, Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"


class StatusCatadorEnum(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"


# EMPRESA SCHEMAS
class EmpresaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=18)
    endereco: str = Field(..., min_length=10, max_length=500)
    telefone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    status: Optional[StatusEmpresaEnum] = StatusEmpresaEnum.ATIVA

    @validator('cnpj')
    def validate_cnpj(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return v

    @validator('telefone')
    def validate_telefone(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
            raise ValueError(
                'Telefone deve ter entre 10 e 13 dígitos'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "EcoColeta Ltda",
                "cnpj": "12.345.678/0001-90",
                "endereco": "Av Paulista, 1000 - São Paulo/SP",
                "telefone": "11987654321",
                "email": "contato@ecocoleta.com.br",
                "status": "ATIVA"
            }
        }


class EmpresaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    endereco: Optional[str] = Field(
        None, min_length=10, max_length=500
    )
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    status: Optional[StatusEmpresaEnum] = None

    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            apenas_numeros = re.sub(r'\D', '', v)
            if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
                raise ValueError(
                    'Telefone deve ter entre 10 e 13 dígitos'
                )
        return v


class EmpresaResponse(BaseModel):
    id: int
    nome: str
    cnpj: str
    endereco: str
    telefone: str
    email: str
    status: StatusEmpresaEnum
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# PONTO DE COLETA SCHEMAS
class PontoColetaCreate(BaseModel):
    empresa_id: int
    nome: str = Field(..., min_length=3, max_length=255)
    endereco: str = Field(..., min_length=10, max_length=500)
    horario_funcionamento: str = Field(
        ..., min_length=5, max_length=255
    )
    telefone: str = Field(..., min_length=10, max_length=20)
    status: Optional[StatusPontoColetaEnum] = (
        StatusPontoColetaEnum.ABERTO
    )

    @validator('telefone')
    def validate_telefone(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
            raise ValueError(
                'Telefone deve ter entre 10 e 13 dígitos'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "empresa_id": 1,
                "nome": "Ponto Central",
                "endereco": (
                    "Rua das Flores, 123 - Centro - "
                    "São Paulo/SP"
                ),
                "horario_funcionamento": (
                    "Segunda a Sexta: 08h às 18h"
                ),
                "telefone": "11987654321",
                "status": "ABERTO"
            }
        }


class PontoColetaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    endereco: Optional[str] = Field(
        None, min_length=10, max_length=500
    )
    horario_funcionamento: Optional[str] = Field(
        None, min_length=5, max_length=255
    )
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    status: Optional[StatusPontoColetaEnum] = None

    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            apenas_numeros = re.sub(r'\D', '', v)
            if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
                raise ValueError(
                    'Telefone deve ter entre 10 e 13 dígitos'
                )
        return v


class PontoColetaResponse(BaseModel):
    id: int
    empresa_id: int
    nome: str
    endereco: str
    horario_funcionamento: str
    telefone: str
    status: StatusPontoColetaEnum
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# CATADOR SCHEMAS
class CatadorCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=14)
    telefone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    status: Optional[StatusCatadorEnum] = StatusCatadorEnum.ATIVO
    empresas_ids: Optional[List[int]] = []

    @validator('cpf')
    def validate_cpf(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v

    @validator('telefone')
    def validate_telefone(cls, v):
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
            raise ValueError(
                'Telefone deve ter entre 10 e 13 dígitos'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João da Silva",
                "cpf": "123.456.789-00",
                "telefone": "11987654321",
                "email": "joao@email.com",
                "status": "ATIVO",
                "empresas_ids": [1, 2]
            }
        }


class CatadorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    telefone: Optional[str] = Field(
        None, min_length=10, max_length=20
    )
    email: Optional[EmailStr] = None
    status: Optional[StatusCatadorEnum] = None
    empresas_ids: Optional[List[int]] = None

    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            apenas_numeros = re.sub(r'\D', '', v)
            if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
                raise ValueError(
                    'Telefone deve ter entre 10 e 13 dígitos'
                )
        return v


# Schema simplificado de empresa para evitar recursão
class EmpresaSimples(BaseModel):
    id: int
    nome: str
    cnpj: str
    status: str

    class Config:
        from_attributes = True


# Schema simplificado de catador para evitar recursão
class CatadorSimples(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    status: StatusCatadorEnum

    class Config:
        from_attributes = True


class CatadorResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    email: Optional[str]
    status: StatusCatadorEnum
    created_at: datetime
    updated_at: Optional[datetime]
    empresas: List[EmpresaSimples] = []

    class Config:
        from_attributes = True

class SolicitacaoColetaUpdate(BaseModel):
    nome_solicitante: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = Field(None, min_length=10, max_length=20)
    quantidade_itens: Optional[int] = Field(None, gt=0)
    endereco: Optional[str] = Field(None, min_length=10, max_length=500)
    foto_url: Optional[str] = Field(None, max_length=500)

    @validator('whatsapp')
    def validate_whatsapp(cls, v):
        if v:
            apenas_numeros = re.sub(r'\D', '', v)
            if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
                raise ValueError(
                    'WhatsApp deve ter entre 10 e 13 dígitos'
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nome_solicitante": "João Silva Santos",
                "email": "novoemail@exemplo.com",
                "whatsapp": "11987654321",
                "quantidade_itens": 10,
                "endereco": "Rua Nova, 456 - Bairro - Cidade/UF",
                "foto_url": "https://storage.exemplo.com/fotos/67890.jpg"
            }
        }


class SolicitacaoColetaList(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[SolicitacaoColetaResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 50,
                "skip": 0,
                "limit": 10,
                "items": [
                    {
                        "id": 1,
                        "nome_solicitante": "João Silva",
                        "tipo_pessoa": "PF",
                        "documento": "123.456.789-00",
                        "email": "cliente@exemplo.com",
                        "whatsapp": "11987654321",
                        "quantidade_itens": 5,
                        "endereco": "Rua Exemplo, 123",
                        "foto_url": "https://storage.exemplo.com/fotos/12345.jpg",
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "created_at": "2025-11-02T10:30:00Z",
                        "ordem_servico_id": 1,
                        "numero_os": "OS-2025-00001"
                    }
                ]
            }
        }
