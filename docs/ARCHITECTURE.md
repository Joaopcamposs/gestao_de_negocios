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
gestao_de_negocios/
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
│       ├── docker-compose.infra.yml    # Postgres compartilhado (rede gestao_de_negocios_network)
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
from messagebus.unity_of_work import UnitOfWork
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
docker-compose.infra.yml     → Postgres compartilhado (rede gestao_de_negocios_network, porta 54322)
docker-compose.dentist.yml   → Dentist API (porta 8001, rede externa gestao_de_negocios_network)
docker-compose.lawyer.yml    → Lawyer API (porta 8002, rede externa gestao_de_negocios_network)
```

- **Postgres é compartilhado** via rede Docker externa (`gestao_de_negocios_network`).
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


---

## Domínio: User

### Campos do Agregado User

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | UUID | ✅ | Identificador único (uuid7) |
| `company` | UUID | ✅ | Empresa associada |
| `email` | str | ✅ | Email de acesso |
| `cpf` | str | ✅ | CPF do usuário |
| `name` | str | ✅ | Nome completo |
| `phone` | str | ✅ | Telefone de contato |
| `street` | str | ✅ | Logradouro (parte do endereço) |
| `number` | str | ✅ | Número do imóvel |
| `zip_code` | str | ✅ | CEP |
| `district` | str | ✅ | Bairro |
| `city` | str | ✅ | Cidade |
| `state` | str | ✅ | Estado |
| `country` | str | ✅ | País |
| `complement` | str | ❌ | Complemento (apto, sala, etc.) |
| `birth_date` | date | ❌ | Data de nascimento |
| `admin` | bool | ✅ | Se é administrador |
| `is_owner` | bool | ❌ | Se é proprietário da empresa |

### Value Object: Address

`shared_core/domain/value_objects/address.py`

Objeto de valor imutável (`frozen=True`) que encapsula o endereço completo. O agregado `User` armazena os campos de endereço de forma plana (para compatibilidade com ORM) e expõe o endereço via propriedade:

```python
user.address  # → Address(street, number, zip_code, district, city, state, country, complement)
```

Tanto `create_aggregate()` quanto `update()` aceitam um objeto `Address`:

```python
address = Address(street="Av. Paulista", number="1000", zip_code="01310100",
                  district="Bela Vista", city="São Paulo", state="SP", country="Brasil",
                  complement="Apto 42")

user = User.create_aggregate(..., address=address)
user.update(address=new_address)
```

---

## Adapters: Billing (Cobrança de Assinatura)

### Estrutura

```
shared_core/adapters/billing/
    abstract_billing.py   # ABC com métodos abstratos
    fake_billing.py       # Implementação fake para testes
```

### AbstractBillingService

Interface em `shared_core/adapters/billing/abstract_billing.py` com os métodos:

| Método | Descrição |
|--------|-----------|
| `create_customer(company_id, email, name)` | Cria cliente no provedor externo |
| `create_subscription(customer_id, price_id)` | Cria assinatura recorrente |
| `cancel_subscription(subscription_id)` | Cancela assinatura |
| `charge_now(customer_id, amount_cents, currency, description)` | Cobrança avulsa imediata |
| `get_subscription_status(subscription_id)` | Consulta status da assinatura |

**Implementação real sugerida**: [Stripe](https://stripe.com/docs/api)
- Instalar: `pip install stripe`
- Variável de ambiente: `STRIPE_API_KEY`
- Usar: `stripe.Customer`, `stripe.Subscription`, `stripe.PaymentIntent`

### FakeBillingService

Implementação em `shared_core/adapters/billing/fake_billing.py` para testes:
- Não realiza cobranças reais
- Armazena operações em `self.customers`, `self.subscriptions`, `self.charges`, `self.cancelled_subscriptions`
- Retorna respostas de sucesso simuladas com IDs `fake_cus_*`, `fake_sub_*`, `fake_ch_*`

```python
billing = FakeBillingService()
customer = await billing.create_customer(company_id, "email@test.com", "Empresa")
result = await billing.create_subscription(customer.external_id, "price_monthly")
assert result.status == "active"
assert len(billing.subscriptions) == 1
```

---

## Adapters: Email (Envio de Emails)

### Estrutura

```
shared_core/adapters/email/
    abstract_email.py   # ABC com métodos abstratos
    fake_email.py       # Implementação fake para testes
```

### AbstractEmailService

Interface em `shared_core/adapters/email/abstract_email.py` com os métodos:

| Método | Descrição |
|--------|-----------|
| `send(message: EmailMessage)` | Envia email genérico |
| `send_welcome(to, name)` | Email de boas-vindas |
| `send_payment_overdue(to, company_name, due_date, amount)` | Aviso de pagamento em atraso |
| `send_account_deactivated(to, company_name)` | Notificação de conta suspensa |
| `send_password_reset(to, reset_token)` | Redefinição de senha |

**Implementação real sugerida**: [SendGrid](https://docs.sendgrid.com/api-reference/mail-send/mail-send)
- Instalar: `pip install sendgrid`
- Variável de ambiente: `SENDGRID_API_KEY`
- Alternativas: Amazon SES (`boto3`), Mailgun, Resend

### FakeEmailService

Implementação em `shared_core/adapters/email/fake_email.py` para testes:
- Não envia emails reais
- Armazena todas as mensagens em `self.sent: list[EmailMessage]`
- Retorna `EmailResult(success=True, message_id="fake_msg_*")`

```python
email_svc = FakeEmailService()
await email_svc.send_welcome("user@test.com", "João")
assert len(email_svc.sent) == 1
assert email_svc.sent[0].subject == "Bem-vindo ao sistema de gestão!"
```

---

## Melhorias

## Otimizações aplicadas

### [.dockerignore](cci:7://file:///Users/joaopcamposs/Dev/gestao_de_negocios/.dockerignore:0:0-0:0) — Build context ~190MB menor
Excluídos: `.venv/`, `.git/`, `tests/`, `docs/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.env`

### [Dockerfile.service](cci:7://file:///Users/joaopcamposs/Dev/gestao_de_negocios/infra/applications/Dockerfile.service:0:0-0:0) — Multi-stage build

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Imagem final** | 1.1GB | 246MB |
| **Rebuild (cache)** | ~15s | ~1.7s |
| **apt build-essential** | Instalado (produção) | Removido |
| **Dev deps** (ruff, mypy, pytest) | Incluídas | Excluídas |
| **Stages** | 1 | 2 (deps + final) |
| **Layer caching** | Nenhum (COPY . . antes de deps) | [pyproject.toml](cci:7://file:///Users/joaopcamposs/Dev/gestao_de_negocios/pyproject.toml:0:0-0:0) copiado primeiro |

### Como funciona o cache
1. **Stage `deps`** — copia só [pyproject.toml](cci:7://file:///Users/joaopcamposs/Dev/gestao_de_negocios/pyproject.toml:0:0-0:0) + `uv.lock` → instala deps → **cacheado enquanto deps não mudam**
2. **Stage final** — copia venv pronta + código-fonte → **rebuild em <2s quando só muda código**