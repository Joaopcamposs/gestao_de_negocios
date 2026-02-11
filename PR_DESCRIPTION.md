# feat: Arquitetura Multi-Serviço com Barramento Independente

## Resumo

Refatoração completa do projeto para uma arquitetura **multi-serviço** com deploy independente por profissão, barramento de mensagens **totalmente desacoplado** e infraestrutura centralizada. Inclui dois microserviços de exemplo: **Dentist** (gestão de pacientes) e **Lawyer** (gestão de processos jurídicos).

## Motivação

O projeto original era monolítico com acoplamento entre o barramento de mensagens e a infraestrutura de banco de dados. A nova arquitetura permite:

- Deploy independente por serviço (dentista, advogado, etc.)
- Barramento de mensagens como lib pura, sem dependências externas
- Isolamento de dados por serviço (database separado) e por empresa (schema separado)
- Escalabilidade horizontal por serviço

## Mudanças Principais

### 🔌 Desacoplamento do MessageBus
- `messagebus/` agora tem **zero imports** de `infra/`, `sqlalchemy`, `shared_core/` ou `services/`
- `AbstractUnitOfWork` usa tipos genéricos (`Any`) em vez de `AsyncSession`
- `DomainRepository` e `ViewRepository` desacoplados de ORM
- Implementação concreta (`UnitOfWork`) movida para `infra/database/unit_of_work.py`

### 📦 Reestruturação do Projeto
- `business_contexts/` → renomeado para `shared_core/` (core compartilhado)
- `UserSecurity` movido de `messagebus/entities.py` → `shared_core/security.py`
- `domains.py`, `handlers.py`, `bootstrap.py` movidos de `messagebus/` → `shared_core/`
- Diretório `entitites/` corrigido para `entities/`

### 🏥 Microserviço Dentist (`services/dentist/`)
- **Domínio**: Patient (nome, CPF, telefone, data de nascimento, observações)
- **Endpoints**: CRUD em `/v1/dentist/patient`
- **Porta**: 8001
- **Database**: `db_dentist`

### ⚖️ Microserviço Lawyer (`services/lawyer/`)
- **Domínio**: LegalCase (número do processo, cliente, descrição, status, data de abertura)
- **Endpoints**: CRUD em `/v1/lawyer/case`
- **Porta**: 8002
- **Database**: `db_lawyer`

### 🗄️ Multi-Database
- `infra/database/service_registry.py` — mapeia `service_type` → database name
- Session factory e engine suportam parâmetro `service_type`
- Cache de engines por database (substituiu engine global única)
- `init-databases.sql` cria `db_dentist` e `db_lawyer` automaticamente

### 🐳 Infraestrutura Docker
- Postgres compartilhado em `docker-compose.infra.yml` com rede Docker externa
- Cada serviço tem seu próprio `docker-compose.<nome>.yml` usando a rede compartilhada
- Sem conflitos de porta ou container name ao rodar múltiplos serviços
- `Dockerfile.service` genérico com `SERVICE_MODULE` parametrizável

### 📋 Makefile Completo
- `make deploy-core/dentist/lawyer` — deploy individual (auto sobe infra)
- `make deploy-all` / `stop-all` — gestão em lote
- `make run-core/dentist/lawyer` — dev local sem Docker
- `make test-dentist/lawyer` — testes isolados por serviço
- `make help` — documentação inline de todos os comandos

## Testes

| Tipo | Quantidade | Status |
|------|-----------|--------|
| Unitários | 152 | ✅ |
| Integração | 80 | ✅ |
| **Total** | **232** | **✅** |

## Arquitetura

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Core API   │   │  Dentist    │   │   Lawyer    │
│  :8000      │   │  :8001      │   │   :8002     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                  │
       └────────┬────────┘──────────────────┘
                │
    ┌───────────┴───────────┐
    │   shared_core (lib)   │
    │   messagebus  (lib)   │  ← independente
    │   infra (database)    │
    └───────────┬───────────┘
                │
    ┌───────────┴───────────┐
    │ PostgreSQL            │
    │  ├── db_dentist       │
    │  ├── db_lawyer        │
    │  └── ...              │
    └───────────────────────┘
```

## Breaking Changes

- `from messagebus.unity_of_work import UnitOfWork` → `from infra.database.unit_of_work import UnitOfWork`
- `business_contexts` → `shared_core` (todos os imports)
- `messagebus.entities.UserSecurity` → `shared_core.security.UserSecurity`
- Docker compose files movidos para `infra/applications/`
- Comandos do Makefile renomeados (`compose` → `deploy-core`, etc.)

## Checklist

- [x] MessageBus totalmente independente (zero imports de infra)
- [x] UnitOfWork concreto movido para `infra/database/unit_of_work.py`
- [x] `shared_core/` substituindo `business_contexts/`
- [x] Serviço Dentist com Patient (CRUD + testes)
- [x] Serviço Lawyer com LegalCase (CRUD + testes)
- [x] Docker Compose por serviço com Postgres compartilhado
- [x] Makefile com gestão independente por serviço
- [x] 232 testes passando (152 unit + 80 integration)
- [x] README e ARCHITECTURE.md atualizados
- [x] Deploy verificado (3 serviços rodando simultaneamente em portas diferentes)
