# Arquitetura Multi-Service com Core Compartilhado

## Visão Geral

Plataforma multi-serviço para gerenciamento de clientes de diferentes profissões (dentistas, advogados, esteticistas, etc.).
Cada profissão é um **microserviço independente** com deploy isolado, mas todos compartilham:

- **messagebus/** — Barramento de mensagens (**totalmente independente**, zero dependências de infra/ORM)
- **shared_core/** — Código compartilhado (usuários, auth, empresa)
- **infra/** — Infraestrutura comum (database, UoW concreto, docker)

---

## Estrutura do Monorepo

```
barramento_de_mensagens/
│
├── messagebus/                         # LIB INDEPENDENTE (zero imports de infra/sqlalchemy)
│   ├── messagebus.py                   # MessageBus, Command, Event
│   ├── bootstrap.py                    # Bootstrap com injeção de dependências
│   ├── unity_of_work.py                # AbstractUnitOfWork (somente abstrações)
│   └── entities.py                     # Aggregate, DomainRepository, ViewRepository, UserBase
│
├── shared_core/                        # CORE COMPARTILHADO
│   ├── main.py                         # App FastAPI do core
│   ├── bootstrap.py                    # Bootstrap do core
│   ├── security.py                     # UserSecurity (AES-GCM, hash)
│   ├── domains.py                      # Enum Domain do core
│   ├── handlers.py                     # Registro de handlers (company, user, auth)
│   ├── consts.py                       # Variáveis de ambiente
│   ├── domain/
│   │   ├── aggregate/                  # Company, User, PublicUser
│   │   ├── commands/                   # CreateCompany, CreateUser, AuthenticateUser
│   │   ├── events/                     # CompanyCreated, UserCreated, etc.
│   │   ├── entities/                   # Entidades de leitura
│   │   └── excecoes.py                 # Exceções de domínio
│   ├── adapters/
│   │   ├── orm/                        # Mapeamentos ORM (company, user, public_user)
│   │   ├── repository/                 # Repositórios de escrita e leitura
│   │   └── views/                      # Views de consulta
│   ├── entrypoints/
│   │   ├── api/                        # Routers FastAPI (company, user, security)
│   │   └── schemas/                    # Schemas Pydantic
│   └── services/
│       └── handlers/                   # Handlers de comandos e eventos
│
├── services/                           # MICROSERVIÇOS ISOLADOS
│   ├── dentist/                        # Gestão para Dentistas (porta 8001)
│   │   ├── domain/                     # Patient (aggregate, commands, events, entities, exceptions)
│   │   ├── adapters/                   # ORM, repositórios, views
│   │   ├── entrypoints/               # API (/v1/dentist/patient), schemas
│   │   ├── services/handlers/          # Handlers de Patient
│   │   ├── domains.py                  # DentistDomain enum
│   │   ├── handlers.py                 # Core + dentist handlers
│   │   ├── bootstrap.py                # bootstrap_dentist(SERVICE_TYPE="dentist")
│   │   └── main.py                     # App FastAPI
│   │
│   └── lawyer/                         # Gestão para Advogados (porta 8002)
│       ├── domain/                     # LegalCase (aggregate, commands, events, entities, exceptions)
│       ├── adapters/                   # ORM, repositórios, views
│       ├── entrypoints/               # API (/v1/lawyer/case), schemas
│       ├── services/handlers/          # Handlers de LegalCase
│       ├── domains.py                  # LawyerDomain enum
│       ├── handlers.py                 # Core + lawyer handlers
│       ├── bootstrap.py                # bootstrap_lawyer(SERVICE_TYPE="lawyer")
│       └── main.py                     # App FastAPI
│
├── infra/
│   ├── database/                       # Infraestrutura de banco de dados
│   │   ├── __init__.py                 # Engine, session factory, mapper registry
│   │   ├── unit_of_work.py             # UnitOfWork concreto (SQLAlchemy)
│   │   ├── service_registry.py         # Mapeamento service_type → database
│   │   ├── schema_handlers.py          # Criação de schemas multi-tenant
│   │   └── initializers.py             # Inicialização da primeira empresa
│   └── applications/                   # Docker e deploy
│       ├── docker-compose.infra.yml    # Postgres compartilhado (rede barramento_network)
│       ├── docker-compose.dentist.yml  # Dentist API (:8001)
│       ├── docker-compose.lawyer.yml   # Lawyer API (:8002)
│       ├── docker-compose.test.yml     # Postgres de testes (:54323)
│       ├── Dockerfile.service          # Imagem genérica para microserviços
│       └── init-databases.sql          # Criação dos databases (db_dentist, db_lawyer)
│
├── libs/basic_types.py                 # CPF, CNPJ, Email
├── tests/                              # 232 testes (152 unit + 80 integration)
├── pyproject.toml
└── Makefile                            # Gestão de serviços, deploy e testes
```

---

## Desacoplamento do MessageBus

O `messagebus/` é **totalmente independente**:

- **Zero imports** de `infra/`, `shared_core/`, `services/`, ou `sqlalchemy`.
- `AbstractUnitOfWork` usa `Any` para tipos de sessão (sem depender de ORM).
- `DomainRepository` e `ViewRepository` usam `Any` para sessões.
- A implementação concreta (`UnitOfWork` com SQLAlchemy) está em `infra/database/unit_of_work.py`.

### Padrão de Import

```python
# No messagebus (abstrações puras)
from messagebus.unity_of_work import AbstractUnitOfWork

# No código de aplicação (implementação concreta)
from infra.database.unit_of_work import UnitOfWork
```

---

## Estratégia de Banco de Dados

### Regras

1. **Um database por tipo de serviço**: `db_dentist`, `db_lawyer`, etc.
2. **Schemas por tenant (empresa)** dentro de cada database.
3. **Tabela `public_user` no schema `public`** — para autenticação cross-tenant.
4. **Tabelas privadas** (user, company, etc.) dentro do schema do tenant.

### Fluxo de Resolução de Database

```
Request → JWT decode → { service_type, company_id }
                              │              │
                              ▼              ▼
                      resolve database   set schema
                      (db_dentist)       (company_uuid)
```

### service_registry.py

```python
SERVICE_DATABASES = {
    "dentist": {"db_name": "db_dentist"},
    "lawyer":  {"db_name": "db_lawyer"},
}
```

---

## Docker e Deploy

### Arquitetura Docker

```
docker-compose.infra.yml     → Postgres compartilhado (rede barramento_network, porta 54322)
docker-compose.dentist.yml   → Dentist API (porta 8001, rede externa barramento_network)
docker-compose.lawyer.yml    → Lawyer API (porta 8002, rede externa barramento_network)
```

- **Postgres é compartilhado** via rede Docker externa (`barramento_network`).
- Cada serviço conecta à mesma instância Postgres, mas usa databases diferentes.
- `deploy-*` chama `infra-up` automaticamente como dependência.

### Independência de Deploy

- Alterar código do dentist **não afeta** o lawyer.
- Cada serviço tem seu próprio `main.py`, `Dockerfile`, `docker-compose`.
- O `shared_core` e `messagebus` são importados como módulos Python locais (monorepo).

---

## Como Criar um Novo Microserviço

1. Criar pasta `services/<nome>/` com a estrutura padrão.
2. Registrar database em `infra/database/service_registry.py`.
3. Adicionar SQL em `infra/applications/init-databases.sql`.
4. Criar `domains.py` — enum mapeando domínios para repositórios.
5. Criar `handlers.py` — combinar handlers do `shared_core` + específicos.
6. Criar `bootstrap.py` — inicializar MessageBus com `SERVICE_TYPE="<nome>"`.
7. Criar `main.py` — app FastAPI incluindo routers do core + específicos.
8. Criar `infra/applications/docker-compose.<nome>.yml`.
9. Adicionar ao Makefile: `deploy-<nome>`, `stop-<nome>`, `logs-<nome>`, `test-<nome>`.
10. Criar testes em `tests/unit/test_services/test_<nome>/` e `tests/integration/test_services/test_<nome>/`.
11. Registrar ORM no `tests/integration/conftest.py`.

---

## Princípios

- **MessageBus independente** — zero dependências de infra, pode ser extraído como pacote.
- **UoW abstrato no messagebus, concreto na infra** — inversão de dependência.
- **Contextos isolados** — cada serviço tem domínio, handlers, API e deploy próprios.
- **Core compartilhado** — User, Company, Auth são reutilizados por todos.
- **Database por serviço, schema por tenant** — isolamento total de dados.
- **Código em inglês, docstrings em português** — padrão do projeto.
- **Tipagem forte** — type hints em todo o código.
- **Testes sempre** — unitários + integração para cada contexto.


## Melhorias

## Otimizações aplicadas

### [.dockerignore](cci:7://file:///Users/joaopcamposs/Dev/barramento_de_mensagens/.dockerignore:0:0-0:0) — Build context ~190MB menor
Excluídos: `.venv/`, `.git/`, `tests/`, `docs/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.env`

### [Dockerfile.service](cci:7://file:///Users/joaopcamposs/Dev/barramento_de_mensagens/infra/applications/Dockerfile.service:0:0-0:0) — Multi-stage build

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Imagem final** | 1.1GB | 246MB |
| **Rebuild (cache)** | ~15s | ~1.7s |
| **apt build-essential** | Instalado (produção) | Removido |
| **Dev deps** (ruff, mypy, pytest) | Incluídas | Excluídas |
| **Stages** | 1 | 2 (deps + final) |
| **Layer caching** | Nenhum (COPY . . antes de deps) | [pyproject.toml](cci:7://file:///Users/joaopcamposs/Dev/barramento_de_mensagens/pyproject.toml:0:0-0:0) copiado primeiro |

### Como funciona o cache
1. **Stage `deps`** — copia só [pyproject.toml](cci:7://file:///Users/joaopcamposs/Dev/barramento_de_mensagens/pyproject.toml:0:0-0:0) + `uv.lock` → instala deps → **cacheado enquanto deps não mudam**
2. **Stage final** — copia venv pronta + código-fonte → **rebuild em <2s quando só muda código**