Nova entidade:

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

class StatusCatador(str, enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"

# Tabela associativa para relacionamento muitos-para-muitos
catadores_empresas = Table(
    'catadores_empresas',
    Base.metadata,
    Column('catador_id', Integer, ForeignKey('catadores.id'), primary_key=True),
    Column('empresa_id', Integer, ForeignKey('empresas.id'), primary_key=True),
    Column('data_vinculo', DateTime(timezone=True), server_default=func.now(), nullable=False)
)


class Catador(Base):
    __tablename__ = "catadores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    status = Column(SQLEnum(StatusCatador), default=StatusCatador.ATIVO, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento muitos-para-muitos
    empresas = relationship("Empresa", secondary=catadores_empresas, back_populates="catadores")

    def __repr__(self):
        return f"<Catador(id={self.id}, nome={self.nome})>"

Schemas Pydantic:

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime
import re

class StatusCatadorEnum(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"

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
            raise ValueError('Telefone deve ter entre 10 e 13 dígitos')
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
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    status: Optional[StatusCatadorEnum] = None
    empresas_ids: Optional[List[int]] = None

    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            apenas_numeros = re.sub(r'\D', '', v)
            if len(apenas_numeros) < 10 or len(apenas_numeros) > 13:
                raise ValueError('Telefone deve ter entre 10 e 13 dígitos')
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


Atualização na classe Empresa (adicione apenas o relacionamento):

# Adicionar dentro da classe Empresa existente:
    # Relacionamento muitos-para-muitos (adicionar junto com os outros relacionamentos)
    catadores = relationship("Catador", secondary=catadores_empresas, back_populates="empresas")


endpoint basico:

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router_catadores = APIRouter(prefix="/catadores", tags=["Catadores"])

@router_catadores.post("/", response_model=CatadorResponse, status_code=201)
def criar_catador(
    catador: CatadorCreate,
    db: Session = Depends(get_db)
):
    # Verificar se CPF já existe
    catador_existente = db.query(Catador).filter(Catador.cpf == catador.cpf).first()
    if catador_existente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Criar catador
    catador_data = catador.dict(exclude={'empresas_ids'})
    db_catador = Catador(**catador_data)
    
    # Vincular empresas se foram fornecidas
    if catador.empresas_ids:
        empresas = db.query(Empresa).filter(Empresa.id.in_(catador.empresas_ids)).all()
        if len(empresas) != len(catador.empresas_ids):
            raise HTTPException(status_code=404, detail="Uma ou mais empresas não encontradas")
        db_catador.empresas = empresas
    
    db.add(db_catador)
    db.commit()
    db.refresh(db_catador)
    return db_catador

@router_catadores.get("/", response_model=List[CatadorResponse])
def listar_catadores(
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusCatadorEnum] = None,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Catador)
    
    if status:
        query = query.filter(Catador.status == status)
    
    if empresa_id:
        # Filtrar catadores que trabalham em uma empresa específica
        query = query.join(Catador.empresas).filter(Empresa.id == empresa_id)
    
    catadores = query.offset(skip).limit(limit).all()
    return catadores

@router_catadores.get("/{catador_id}", response_model=CatadorResponse)
def obter_catador(catador_id: int, db: Session = Depends(get_db)):
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    return catador

@router_catadores.put("/{catador_id}", response_model=CatadorResponse)
def atualizar_catador(
    catador_id: int,
    catador_update: CatadorUpdate,
    db: Session = Depends(get_db)
):
    db_catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not db_catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    update_data = catador_update.dict(exclude_unset=True, exclude={'empresas_ids'})
    for key, value in update_data.items():
        setattr(db_catador, key, value)
    
    # Atualizar empresas se fornecido
    if catador_update.empresas_ids is not None:
        empresas = db.query(Empresa).filter(Empresa.id.in_(catador_update.empresas_ids)).all()
        if len(empresas) != len(catador_update.empresas_ids):
            raise HTTPException(status_code=404, detail="Uma ou mais empresas não encontradas")
        db_catador.empresas = empresas
    
    db.commit()
    db.refresh(db_catador)
    return db_catador

@router_catadores.delete("/{catador_id}", status_code=204)
def deletar_catador(catador_id: int, db: Session = Depends(get_db)):
    db_catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not db_catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    db.delete(db_catador)
    db.commit()
    return

# Endpoints para gerenciar o vínculo entre catador e empresa
@router_catadores.post("/{catador_id}/empresas/{empresa_id}", status_code=204)
def vincular_empresa(
    catador_id: int,
    empresa_id: int,
    db: Session = Depends(get_db)
):
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    if empresa in catador.empresas:
        raise HTTPException(status_code=400, detail="Catador já vinculado a esta empresa")
    
    catador.empresas.append(empresa)
    db.commit()
    return

@router_catadores.delete("/{catador_id}/empresas/{empresa_id}", status_code=204)
def desvincular_empresa(
    catador_id: int,
    empresa_id: int,
    db: Session = Depends(get_db)
):
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    if empresa not in catador.empresas:
        raise HTTPException(status_code=400, detail="Catador não está vinculado a esta empresa")
    
    catador.empresas.remove(empresa)
    db.commit()
    return

@router_catadores.get("/{catador_id}/empresas", response_model=List[EmpresaSimples])
def listar_empresas_catador(catador_id: int, db: Session = Depends(get_db)):
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    return catador.empresas

Endpoints adicionais para Empresas (adicionar no router de empresas):

# Adicionar no router_empresas existente

@router_empresas.get("/{empresa_id}/catadores", response_model=List[CatadorSimples])
def listar_catadores_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa.catadores

@router_empresas.post("/{empresa_id}/catadores/{catador_id}", status_code=204)
def vincular_catador(
    empresa_id: int,
    catador_id: int,
    db: Session = Depends(get_db)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    if catador in empresa.catadores:
        raise HTTPException(status_code=400, detail="Catador já vinculado a esta empresa")
    
    empresa.catadores.append(catador)
    db.commit()
    return

@router_empresas.delete("/{empresa_id}/catadores/{catador_id}", status_code=204)
def desvincular_catador(
    empresa_id: int,
    catador_id: int,
    db: Session = Depends(get_db)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    catador = db.query(Catador).filter(Catador.id == catador_id).first()
    if not catador:
        raise HTTPException(status_code=404, detail="Catador não encontrado")
    
    if catador not in empresa.catadores:
        raise HTTPException(status_code=400, detail="Catador não está vinculado a esta empresa")
    
    empresa.catadores.remove(catador)
    db.commit()
    return