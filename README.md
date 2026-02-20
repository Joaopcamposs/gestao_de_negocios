# Barramento de Mensagens — Plataforma Multi-Serviço

Plataforma multi-serviço para gerenciamento de clientes de diferentes profissões, implementada com **Python 3.11**, **FastAPI**, **SQLAlchemy** (async) e **PostgreSQL**. Segue os padrões de **Domain-Driven Design (DDD)**, **CQRS** e **Event-Driven Architecture**.

Cada profissão é um **microserviço independente** com deploy isolado, compartilhando um barramento de mensagens desacoplado, um core de autenticação/empresa e infraestrutura de banco de dados.

---

## Índice

- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Serviços Disponíveis](#serviços-disponíveis)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Executar](#como-executar)
- [Testes](#testes)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação e Segurança](#autenticação-e-segurança)
- [Como Criar um Novo Microserviço](#como-criar-um-novo-microserviço)
- [Tecnologias](#tecnologias)

---

## Arquitetura

```
┌─────────────┐   ┌─────────────┐
│  Dentist    │   │   Lawyer    │
│  :8001      │   │   :8002     │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
    ┌───────────┴───────────┐
    │   shared_core (lib)   │  ← User, Company, Auth
    │   messagebus  (lib)   │  ← Barramento independente
    │   infra (database)    │  ← Session factory, UoW concreto
    └───────────┬───────────┘
                │
    ┌───────────┴───────────┐
    │ PostgreSQL            │
    │  ├── db_dentist       │
    │  ├── db_lawyer        │
    │  └── ...              │
    └───────────────────────┘
```

### Conceitos-chave

- **MessageBus** — Lib independente (zero dependências externas). Roteia Commands e Events para handlers.
- **Command** — Ação imperativa com um único handler (ex: `CreatePatient`). Retorna resultado.
- **Event** — Notificação com múltiplos handlers (ex: `PatientCreated`). Não retorna resultado.
- **Unit of Work (UoW)** — Gerencia transações e coleta eventos dos agregados. Abstração no messagebus, implementação concreta em `infra/database/`.
- **Bootstrap** — Configura o MessageBus com injeção de dependências nos handlers.
- **Multi-tenancy** — Um database por tipo de serviço, schemas por empresa (tenant) dentro de cada database.

---

## Estrutura do Projeto

```
gestao_de_negocios/
│
├── messagebus/                         # LIB INDEPENDENTE: Barramento de mensagens
│   ├── messagebus.py                   # MessageBus, Command, Event
│   ├── bootstrap.py                    # Bootstrap com injeção de dependências
│   ├── unity_of_work.py                # AbstractUnitOfWork (sem dependências de infra)
│   └── entities.py                     # Aggregate, DomainRepository, ViewRepository, UserBase
│
├── shared_core/                        # CORE COMPARTILHADO: usado por todos os microserviços
│   ├── consts.py                       # Variáveis de ambiente
│   ├── security.py                     # UserSecurity (criptografia AES-GCM)
│   ├── bootstrap.py                    # Bootstrap do core
│   ├── domains.py                      # Enum Domain do core
│   ├── handlers.py                     # Registro de handlers do core
│   ├── domain/
│   │   ├── aggregate/                  # Company, User, PublicUser
│   │   ├── commands/                   # CreateCompany, CreateUser, AuthenticateUser
│   │   ├── events/                     # CompanyCreated, UserCreated, etc.
│   │   ├── entities/                   # Entidades de leitura
│   │   └── excecoes.py                 # Exceções de domínio
│   ├── adapters/
│   │   ├── orm/                        # Mapeamentos ORM
│   │   ├── repository/                 # Repositórios de escrita e leitura
│   │   └── views/                      # Views de consulta
│   ├── entrypoints/
│   │   ├── api/                        # Routers FastAPI (company, user, security)
│   │   └── schemas/                    # Schemas Pydantic
│   └── services/
│       └── handlers/                   # Handlers de comandos e eventos
│
├── services/                           # MICROSERVIÇOS: contextos de negócio isolados
│   ├── dentist/                        # Serviço: Gestão para Dentistas
│   │   ├── domain/aggregate/           # Patient
│   │   ├── domain/commands/            # CreatePatient, UpdatePatient, DeletePatient
│   │   ├── domain/events/              # PatientCreated, PatientUpdated, PatientDeleted
│   │   ├── domain/entities/            # Entidades de leitura
│   │   ├── domain/exceptions.py        # PatientAlreadyRegistered, PatientNotFound
│   │   ├── adapters/orm/              # Mapeamento ORM do Patient
│   │   ├── adapters/repository/        # Repositórios de escrita e leitura
│   │   ├── adapters/views/             # Views de consulta
│   │   ├── entrypoints/api/            # Router FastAPI (/v1/dentist/patient)
│   │   ├── entrypoints/schemas/        # Schemas Pydantic
│   │   ├── services/handlers/          # Handlers de comandos e eventos
│   │   ├── domains.py                  # DentistDomain enum
│   │   ├── handlers.py                 # Combina core + dentist handlers
│   │   ├── bootstrap.py                # bootstrap_dentist()
│   │   └── main.py                     # App FastAPI (porta 8001)
│   │
│   └── lawyer/                         # Serviço: Gestão para Advogados
│       ├── domain/aggregate/           # LegalCase
│       ├── domain/commands/            # CreateLegalCase, UpdateLegalCase, DeleteLegalCase
│       ├── domain/events/              # LegalCaseCreated, LegalCaseUpdated, LegalCaseDeleted
│       ├── adapters/...                # ORM, repositórios, views
│       ├── entrypoints/api/            # Router FastAPI (/v1/lawyer/case)
│       ├── bootstrap.py                # bootstrap_lawyer()
│       └── main.py                     # App FastAPI (porta 8002)
│
├── infra/
│   ├── database/                       # Infraestrutura de banco de dados
│   │   ├── __init__.py                 # Engine, session factory, mapper registry
│   │   ├── unit_of_work.py             # UnitOfWork concreto (SQLAlchemy)
│   │   ├── service_registry.py         # Mapeamento service_type → database
│   │   ├── schema_handlers.py          # Criação de schemas multi-tenant
│   │   └── initializers.py             # Inicialização da primeira empresa
│   └── applications/                   # Docker e deploy
│       ├── docker-compose.infra.yml    # Postgres compartilhado
│       ├── docker-compose.dentist.yml  # Deploy do Dentist API (:8001)
│       ├── docker-compose.lawyer.yml   # Deploy do Lawyer API (:8002)
│       ├── docker-compose.test.yml     # Postgres de testes (:54323)
│       ├── Dockerfile.service          # Imagem genérica para microserviços
│       └── init-databases.sql          # Script de criação dos databases
│
├── tests/
│   ├── unit/                           # 152 testes unitários
│   │   ├── test_company.py
│   │   ├── test_user.py
│   │   ├── test_messagebus.py
│   │   └── test_services/
│   │       ├── test_dentist/
│   │       └── test_lawyer/
│   └── integration/                    # 80 testes de integração
│       ├── conftest.py
│       ├── test_company_integration.py
│       ├── test_user_integration.py
│       ├── test_auth_integration.py
│       └── test_services/
│           ├── test_dentist/
│           └── test_lawyer/
│
├── libs/basic_types.py                 # CPF, CNPJ, Email
├── pyproject.toml                      # Dependências e config
└── Makefile                            # Gestão de serviços e testes
```

---

## Serviços Disponíveis

| Serviço | Porta | Descrição | Domínios |
|---------|-------|-----------|----------|
| **Dentist** | 8001 | Gestão para dentistas | Company, User, Auth + Patient |
| **Lawyer** | 8002 | Gestão para advogados | Company, User, Auth + LegalCase |

Cada serviço inclui automaticamente os endpoints do `shared_core` (empresa, usuário, autenticação) além dos seus endpoints específicos.

---

## Pré-requisitos

- **Python** >= 3.11
- **Docker** e **Docker Compose**
- **uv** (gerenciador de pacotes Python) — instalado automaticamente no Docker

---

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd gestao_de_negocios

# Instale o uv (se ainda não tiver)
pip install uv

# Instale as dependências
uv sync
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto baseado no `.env_example`:

```env
DB_HOST=localhost
DB_PASSWORD=password
DB_USER=postgres
DB_NAME=postgres
DB_NAME_DENTIST=db_dentist
DB_NAME_LAWYER=db_lawyer
FIRST_COMPANY_ID=<uuid>
FIRST_USER_CPF=<cpf>
FIRST_USER_EMAIL=<email>
FIRST_USER_PASSWORD=<password>
ADMIN_USER_PREFIX=admin
AES_KEY=<base64-encoded-32-byte-key>
SECRET_KEY=<jwt-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Como Executar

### Via Docker (recomendado)

```bash
# Ver todos os comandos disponíveis
make help

# Subir toda a infraestrutura + todos os serviços
make deploy-all

# Ou subir serviços individualmente
make deploy-dentist    # Dentist API  → http://localhost:8001/docs
make deploy-lawyer     # Lawyer API   → http://localhost:8002/docs

# Parar tudo
make stop-all

# Parar serviço individual
make stop-dentist
```

### Dev local (sem Docker)

```bash
# Suba o Postgres compartilhado
make infra-up

# Execute cada serviço em terminais separados
make run-dentist       # porta 8001
make run-lawyer        # porta 8002
```

### Gestão de Infraestrutura

```bash
make infra-up          # Sobe Postgres compartilhado (:54322)
make infra-down        # Para Postgres (preserva dados)
make infra-destroy     # Para Postgres e remove volumes
make infra-logs        # Logs do Postgres
```

---

## Testes

```bash
# Testes unitários (152 testes, sem dependências externas)
make test-unit

# Testes de integração (80 testes, sobe/desce PostgreSQL de teste)
make test-integration

# Todos os testes (232 testes)
make test-all

# Testes com cobertura
make test-cov

# Testes de um serviço específico
make test-dentist
make test-lawyer
```

---

## Endpoints da API

### Endpoints Compartilhados (todos os serviços)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Health check |
| POST | `/api/token` | Autentica e retorna token JWT |
| GET | `/api/user/me/` | Retorna dados do usuário autenticado |
| POST | `/v1/company` | Cria uma empresa |
| PUT | `/v1/company` | Atualiza uma empresa |
| GET | `/v1/company` | Lista empresas |
| DELETE | `/v1/company` | Exclui uma empresa |
| POST | `/v1/user` | Cria um usuário |
| PUT | `/v1/user` | Atualiza um usuário |
| GET | `/v1/user` | Lista usuários |
| DELETE | `/v1/user` | Exclui um usuário |

### Dentist API (porta 8001)

#### Patient (`/v1/dentist/patient`)
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/v1/dentist/patient` | Cria um paciente |
| PUT | `/v1/dentist/patient` | Atualiza um paciente |
| GET | `/v1/dentist/patient` | Lista pacientes (filtro por `cpf`) |
| DELETE | `/v1/dentist/patient` | Exclui um paciente |

### Lawyer API (porta 8002)

#### Legal Case (`/v1/lawyer/case`)
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/v1/lawyer/case` | Cria um processo jurídico |
| PUT | `/v1/lawyer/case` | Atualiza um processo |
| GET | `/v1/lawyer/case` | Lista processos (filtro por `case_number`) |
| DELETE | `/v1/lawyer/case` | Exclui um processo |

---

## Autenticação e Segurança

- **JWT** via `PyJWT` com `SECRET_KEY`, `ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **OAuth2** com `OAuth2PasswordBearer` e endpoint `/api/token`.
- **Criptografia AES-GCM** para emails em trânsito, **SHA-256** para hash de busca.
- **bcrypt** para hash de senhas.
- **PublicUser** — tabela no schema `public` para autenticação cross-tenant.
- **Rotas protegidas** — todos os endpoints de negócio exigem autenticação via `Depends(get_current_user)`.

---

## Como Criar um Novo Microserviço

1. **Criar pasta** `services/<nome>/` com a estrutura padrão (domain, adapters, entrypoints, services).
2. **Registrar database** em `infra/database/service_registry.py`:
   ``` python
   SERVICE_DATABASES = {
       ...,
       "<nome>": {"db_name": "db_<nome>"},
   }
   ```
3. **Criar `domains.py`** — enum mapeando domínios para repositórios.
4. **Criar `handlers.py`** — combinar handlers do `shared_core` + handlers específicos.
5. **Criar `bootstrap.py`** — inicializar o MessageBus com `SERVICE_TYPE="<nome>"`.
6. **Criar `main.py`** — app FastAPI incluindo routers do core + específicos.
7. **Criar docker-compose** em `infra/applications/docker-compose.<nome>.yml`.
8. **Adicionar SQL** em `infra/applications/init-databases.sql`:
   ```sql
   SELECT 'CREATE DATABASE db_<nome>' WHERE NOT EXISTS (...);
   ```
9. **Adicionar ao Makefile** — targets `deploy-<nome>`, `stop-<nome>`, `logs-<nome>`, `test-<nome>`.
10. **Criar testes** em `tests/unit/test_services/test_<nome>/` e `tests/integration/test_services/test_<nome>/`.
11. **Registrar ORM** no `tests/integration/conftest.py`.

---

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| **Python 3.11** | Linguagem principal |
| **FastAPI** | Framework web assíncrono |
| **SQLAlchemy 2.0** | ORM com mapeamento imperativo |
| **asyncpg** | Driver async para PostgreSQL |
| **PostgreSQL 16** | Banco de dados relacional |
| **Pydantic** | Validação de schemas |
| **uuid7** | Geração de UUIDs ordenáveis |
| **PyJWT** | Tokens JWT |
| **bcrypt** | Hash de senhas |
| **cryptography** | Criptografia AES-GCM |
| **Sentry SDK** | Monitoramento de erros (produção) |
| **uv** | Gerenciador de pacotes e virtualenv |
| **Docker** | Containerização |
| **pytest** | Framework de testes |
| **Ruff** | Linter e formatter |

---

## Comandos Úteis (Makefile)

```bash
# Infraestrutura
make infra-up            # Sobe Postgres compartilhado
make infra-destroy       # Remove Postgres e volumes

# Deploy
make deploy-all          # Todos os serviços
make deploy-dentist      # Apenas dentista
make stop-all            # Para tudo

# Dev local
make run-dentist         # Dentist na porta 8001
make run-lawyer          # Lawyer na porta 8002

# Testes
make test-unit           # Unitários (152)
make test-integration    # Integração (80)
make test-all            # Todos (232)
make test-cov            # Com cobertura

# Qualidade
make ruff                # Formata e corrige lint
make check               # Lint + type-check
```
