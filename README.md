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
    SOLICITACAO_COLETA ||--o| ORDEM_SERVICO : "gera"
    ORDEM_SERVICO }o--o| EMPRESA : "atribuida_a"
    ORDEM_SERVICO }o--o| PONTO_COLETA : "destinada_a"
    ORDEM_SERVICO }o--o| CATADOR : "executada_por"
    EMPRESA ||--o{ PONTO_COLETA : "possui"
    EMPRESA }o--o{ CATADOR : "vincula"
    
    SOLICITACAO_COLETA {
        int id PK
        string nome_solicitante
        enum tipo_pessoa "PF|PJ"
        string documento "CPF ou CNPJ"
        string email
        string whatsapp
        int quantidade_itens
        enum tipo_material 
        string endereco
        string foto_url "nullable"
        float latitude "nullable"
        float longitude "nullable"
        datetime created_at
        datetime updated_at "nullable"
    }
    
    ORDEM_SERVICO {
        int id PK
        int solicitacao_id FK "unique"
        int empresa_id FK "nullable"
        int ponto_coleta_id FK "nullable"
        int catador_id FK "nullable"
        string numero_os UK "OS-YYYY-NNNNN"
        enum status "PENDENTE|EM_ANDAMENTO|CONCLUIDA|CANCELADA"
        datetime created_at
        datetime updated_at "nullable"
    }
    
    EMPRESA {
        int id PK
        string nome
        string cnpj UK
        string endereco
        string telefone
        string email
        enum status "ATIVA|INATIVA"
        float latitude "nullable"
        float longitude "nullable"
        datetime created_at
        datetime updated_at "nullable"
    }
    
    PONTO_COLETA {
        int id PK
        int empresa_id FK
        string nome
        string endereco
        string horario_funcionamento
        string telefone
        enum status "ABERTO|FECHADO"
        float latitude "nullable"
        float longitude "nullable"
        datetime created_at
        datetime updated_at "nullable"
    }
    
    CATADOR {
        int id PK
        string nome
        string cpf UK
        string telefone
        string email "nullable"
        enum status "ATIVO|INATIVO"
        datetime created_at
        datetime updated_at "nullable"
    }
    
    CATADORES_EMPRESAS {
        int catador_id FK "CASCADE"
        int empresa_id FK "CASCADE"
        datetime data_vinculo
    }
```

## 🔄 Fluxos do Sistema

### Fluxo de Criação de Solicitação

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
    Controller->>DB: INSERT OrdemServico (status: PENDENTE)
    Controller->>DB: COMMIT
    DB-->>Controller: dados salvos
    Controller-->>API: SolicitacaoColetaResponse
    API-->>Cliente: 201 Created
```

### Fluxo de Atribuição de Recursos

```mermaid
sequenceDiagram
    participant Admin
    participant API as FastAPI
    participant Controller as SolicitacoesController
    participant DB as PostgreSQL
    
    Admin->>API: PATCH /ordens-servico/{id}/atribuir
    API->>Controller: atribuir_ordem_servico()
    Controller->>DB: Validar Empresa
    Controller->>DB: Validar PontoColeta
    Controller->>DB: Validar Catador
    Controller->>DB: UPDATE OrdemServico
    Controller->>DB: COMMIT
    DB-->>Controller: OS atualizada
    Controller-->>API: OrdemServicoResponse (completo)
    API-->>Admin: 200 OK
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

### Solicitações de Coleta
- `POST /solicitacoes` - Criar solicitação de coleta (gera OS
  automaticamente)
- `GET /solicitacoes` - Listar solicitações com filtros
  (tipo_pessoa, documento) e paginação
- `GET /solicitacoes/{id}` - Obter detalhes de uma solicitação
- `PATCH /solicitacoes/{id}` - Atualizar solicitação
- `DELETE /solicitacoes/{id}` - Deletar solicitação e OS associada

### Ordens de Serviço
- `GET /solicitacoes/ordens-servico` - Listar ordens de serviço
  com dados completos (solicitação, empresa, ponto de coleta,
  catador, tipo_pessoa PF/PJ) e paginação
- `GET /solicitacoes/ordens-servico/{id}` - Obter detalhes
  completos de uma OS
- `PATCH /solicitacoes/ordens-servico/{id}/status` - Atualizar
  status da OS
- `PATCH /solicitacoes/ordens-servico/{id}/atribuir` - Atribuir
  empresa, ponto de coleta e/ou catador a uma OS
- `DELETE /solicitacoes/ordens-servico/{id}` - Deletar ordem de
  serviço (solicitação permanece)

### Empresas
- `POST /empresas` - Criar empresa
- `GET /empresas` - Listar todas as empresas
- `GET /empresas/{id}` - Obter detalhes de uma empresa
- `PUT /empresas/{id}` - Atualizar empresa
- `DELETE /empresas/{id}` - Deletar empresa
- `GET /empresas/{id}/catadores` - Listar catadores vinculados
  à empresa
- `POST /empresas/{id}/catadores/{catador_id}` - Vincular
  catador à empresa
- `DELETE /empresas/{id}/catadores/{catador_id}` - Desvincular
  catador da empresa

### Pontos de Coleta
- `POST /pontos-coleta` - Criar ponto de coleta
- `GET /pontos-coleta` - Listar todos os pontos de coleta
- `GET /pontos-coleta/{id}` - Obter detalhes de um ponto de
  coleta
- `GET /pontos-coleta/empresa/{empresa_id}` - Listar pontos de
  coleta de uma empresa
- `PUT /pontos-coleta/{id}` - Atualizar ponto de coleta
- `DELETE /pontos-coleta/{id}` - Deletar ponto de coleta

### Catadores
- `POST /catadores` - Criar catador (pode vincular empresas
  na criação)
- `GET /catadores` - Listar catadores com filtros (status,
  empresa_id) e paginação
- `GET /catadores/{id}` - Obter detalhes de um catador
- `PUT /catadores/{id}` - Atualizar catador
- `DELETE /catadores/{id}` - Deletar catador
- `GET /catadores/{id}/empresas` - Listar empresas vinculadas
  ao catador
- `POST /catadores/{catador_id}/empresas/{empresa_id}` -
  Vincular catador à empresa
- `DELETE /catadores/{catador_id}/empresas/{empresa_id}` -
  Desvincular catador da empresa

### Geral
- `GET /` - Status da API

## 🔐 Autenticação

O sistema possui código de autenticação em `/auth`, porém o router
não está registrado no `main.py` atualmente. As rotas disponíveis
no código são:
- `POST /auth/token` - Obter token de acesso (OAuth2)
- `POST /auth/refresh_token` - Renovar token de acesso

> **Nota:** Para usar as rotas de autenticação, é necessário
> registrar o router no `main.py`.

## 🎯 Funcionalidades Principais

- **Gestão de Solicitações**: Criação, atualização e exclusão de
  solicitações de coleta com validação de CPF/CNPJ e geocodificação
  automática
- **Tipo de Material**: Classificação de materiais (METAIS,
  ELETRONICO, PAPEL, PLASTICO, VIDRO, OUTROS)
- **Ordens de Serviço**: Geração automática de OS com numeração
  sequencial por ano (formato: OS-YYYY-NNNNN)
- **Atribuição de Recursos**: Sistema para atribuir empresa,
  ponto de coleta e catador a cada ordem de serviço
- **Filtros Avançados**: Listagem com filtros por tipo de pessoa
  (PF/PJ), documento, status, etc., com paginação
- **Geocodificação**: Integração com OpenStreetMap para obtenção
  de coordenadas a partir de endereços
- **Gestão de Vínculos**: Sistema para vincular/desvincular
  catadores a empresas com integridade referencial (CASCADE)
  automática

## 📄 Sobre o Projeto

Este projeto foi desenvolvido para o hackathon do programa Devs de
Impacto.

### Dados Retornados nas Ordens de Serviço

Ao listar ou consultar uma ordem de serviço, o sistema retorna:

- Dados da **solicitação** (nome, tipo_pessoa PF/PJ, documento,
  tipo_material, endereço, coordenadas)
- **Empresa** atribuída (se houver)
- **Ponto de coleta** atribuído (se houver)
- **Catador** atribuído (se houver)
- Status e informações de data (created_at, updated_at)

### Paginação

A maioria das listagens suporta paginação através dos parâmetros:
- `skip`: Número de registros para pular (padrão: 0)
- `limit`: Limite de registros por página (padrão: 100, máximo: 100)

Exemplo: `GET /solicitacoes?skip=0&limit=10`

### Filtros Disponíveis

- **Solicitações**: `tipo_pessoa`, `documento`
- **Ordens de Serviço**: `status`
- **Catadores**: `status`, `empresa_id`

