# Devs de Impacto - Backend

API REST desenvolvida com FastAPI para gerenciamento de solicitações
de coleta de materiais recicláveis.

## 📋 Tabela de Conteúdo

- [Sobre](#sobre)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Modelos de Dados](#modelos-de-dados)
- [Instalação](#instalação)
- [Uso](#uso)

## 🎯 Sobre

Projeto de backend desenvolvido para hackathon, focado em
gerenciamento de coleta de materiais recicláveis, conectando
empresas, pontos de coleta, catadores e solicitantes.

## 🛠 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Banco de dados relacional
- **Alembic** - Migrações de banco de dados
- **Pydantic** - Validação de dados
- **Poetry** - Gerenciamento de dependências

## 🏗 Arquitetura

```mermaid
graph TB
    Client[Cliente/Frontend] --> FastAPI[FastAPI App]
    
    FastAPI --> Router1["/solicitacoes"]
    FastAPI --> Router2["/empresas"]
    FastAPI --> Router3["/pontos_coleta"]
    FastAPI --> Router4["/catadores"]
    FastAPI --> Router5["/auth"]
    
    Router1 --> Controller1[SolicitacoesController]
    Router2 --> Controller2[EmpresasController]
    Router3 --> Controller3[PontosColetaController]
    Router4 --> Controller4[CatadoresController]
    Router5 --> Controller5[AuthController]
    
    Controller1 --> Schemas[Schemas/Pydantic]
    Controller2 --> Schemas
    Controller3 --> Schemas
    Controller4 --> Schemas
    Controller5 --> Schemas
    
    Controller1 --> Models[Models/SQLAlchemy]
    Controller2 --> Models
    Controller3 --> Models
    Controller4 --> Models
    
    Controller1 --> Geocoding[GeocodingService]
    
    Models --> Database[(PostgreSQL)]
    
    Geocoding --> OSM[OpenStreetMap API]
```

## 📊 Modelos de Dados

```mermaid
erDiagram
    SOLICITACAO_COLETA ||--o| ORDEM_SERVICO : "tem"
    EMPRESA ||--o{ PONTO_COLETA : "possui"
    EMPRESA }o--o{ CATADOR : "vincula"
    
    SOLICITACAO_COLETA {
        int id PK
        string nome_solicitante
        enum tipo_pessoa
        string documento
        string email
        string whatsapp
        int quantidade_itens
        string endereco
        string foto_url
        float latitude
        float longitude
        datetime created_at
    }
    
    ORDEM_SERVICO {
        int id PK
        int solicitacao_id FK
        string numero_os UK
        enum status
        datetime created_at
        datetime updated_at
    }
    
    EMPRESA {
        int id PK
        string nome
        string cnpj UK
        string endereco
        string telefone
        string email
        enum status
        float latitude
        float longitude
        datetime created_at
    }
    
    PONTO_COLETA {
        int id PK
        int empresa_id FK
        string nome
        string endereco
        string horario_funcionamento
        string telefone
        enum status
        float latitude
        float longitude
        datetime created_at
    }
    
    CATADOR {
        int id PK
        string nome
        string cpf UK
        string telefone
        string email
        enum status
        datetime created_at
    }
    
    CATADORES_EMPRESAS {
        int catador_id FK
        int empresa_id FK
        datetime data_vinculo
    }
```

## 🔄 Fluxo de Solicitação de Coleta

```mermaid
sequenceDiagram
    participant Cliente
    participant API as FastAPI
    participant Controller as SolicitacoesController
    participant Geocoding as GeocodingService
    participant DB as PostgreSQL
    
    Cliente->>API: POST /solicitacoes
    API->>Controller: criar_solicitacao_coleta()
    Controller->>Geocoding: geocode_address(endereco)
    Geocoding->>OSM: GET /search
    OSM-->>Geocoding: coordenadas
    Geocoding-->>Controller: {latitude, longitude}
    Controller->>DB: INSERT SolicitacaoColeta
    Controller->>DB: gerar_numero_os()
    Controller->>DB: INSERT OrdemServico
    Controller->>DB: COMMIT
    DB-->>Controller: dados salvos
    Controller-->>API: SolicitacaoColetaResponse
    API-->>Cliente: 201 Created
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.12+
- PostgreSQL
- Poetry

### Passos

1. Clone o repositório
2. Instale as dependências:

```bash
poetry install
```

3. Configure as variáveis de ambiente (`.env`):

```env
DATABASE_URL=postgresql://usuario:senha@localhost/database
```

4. Execute as migrações:

```bash
alembic upgrade head
```

## 💻 Uso

### Desenvolvimento

```bash
poetry run task dev
```

### Executar API

```bash
poetry run task run
```

### Testes

```bash
poetry run task test
```

### Linting

```bash
poetry run task lint
```

> **Nota:** Este é um projeto desenvolvido para hackathon e não
> está configurado para uso em produção.

## 📝 Rotas Principais

- `GET /` - Status da API
- `POST /solicitacoes` - Criar solicitação de coleta
- `GET /solicitacoes` - Listar solicitações
- `GET /solicitacoes/{id}` - Obter solicitação
- `PATCH /solicitacoes/{id}` - Atualizar solicitação
- `GET /solicitacoes/ordens-servico` - Listar ordens de serviço
- `PATCH /solicitacoes/ordens-servico/{id}/status` - Atualizar status
- `POST /empresas` - Criar empresa
- `GET /empresas` - Listar empresas
- `POST /pontos-coleta` - Criar ponto de coleta
- `GET /pontos-coleta` - Listar pontos de coleta
- `POST /catadores` - Criar catador
- `GET /catadores` - Listar catadores

## 🔐 Autenticação

O sistema possui rotas de autenticação em `/auth` para gerenciamento
de usuários e sessões.

## 📄 Sobre o Projeto

Este projeto foi desenvolvido para o hackathon do programa Devs de
Impacto.

