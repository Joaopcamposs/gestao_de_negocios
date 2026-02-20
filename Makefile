export COMPOSE_NAME=gestao_de_negocios
export COMPOSE_TEST_NAME=$(COMPOSE_NAME)_test
export INFRA=infra/applications

# ── Lint & Quality ──────────────────────────────────────────────────
ruff:
	ruff format . && ruff check . --fix

lint: ruff

mypy:
	mypy shared_core/ services/ infra/ messagebus/ libs/

typecheck: mypy

check: lint typecheck
	@echo "✔ Lint (ruff) e type-check (mypy) passaram."

# ── Infra (Postgres compartilhado) ─────────────────────────────────
infra-up:
	docker compose -f $(INFRA)/docker-compose.infra.yml -p $(COMPOSE_NAME)_infra up -d --wait
	@echo "✔ Postgres rodando em localhost:54322"

infra-down:
	docker compose -f $(INFRA)/docker-compose.infra.yml -p $(COMPOSE_NAME)_infra down

infra-destroy:
	docker compose -f $(INFRA)/docker-compose.infra.yml -p $(COMPOSE_NAME)_infra down -v
	@echo "✔ Postgres parado e volumes removidos."

infra-logs:
	docker compose -f $(INFRA)/docker-compose.infra.yml -p $(COMPOSE_NAME)_infra logs -f

# ── Deploy: Dentist (porta 8001) ──────────────────────────────────
deploy-dentist: infra-up
	docker compose -f $(INFRA)/docker-compose.dentist.yml -p $(COMPOSE_NAME)_dentist up --build -d
	@echo "✔ Dentist API rodando em http://localhost:8001/docs"

stop-dentist:
	docker compose -f $(INFRA)/docker-compose.dentist.yml -p $(COMPOSE_NAME)_dentist down

logs-dentist:
	docker compose -f $(INFRA)/docker-compose.dentist.yml -p $(COMPOSE_NAME)_dentist logs -f

# ── Deploy: Lawyer (porta 8002) ───────────────────────────────────
deploy-lawyer: infra-up
	docker compose -f $(INFRA)/docker-compose.lawyer.yml -p $(COMPOSE_NAME)_lawyer up --build -d
	@echo "✔ Lawyer API rodando em http://localhost:8002/docs"

stop-lawyer:
	docker compose -f $(INFRA)/docker-compose.lawyer.yml -p $(COMPOSE_NAME)_lawyer down

logs-lawyer:
	docker compose -f $(INFRA)/docker-compose.lawyer.yml -p $(COMPOSE_NAME)_lawyer logs -f

# ── Deploy: Todos ─────────────────────────────────────────────────
deploy-all: deploy-dentist deploy-lawyer
	@echo ""
	@echo "  ✔ Todos os serviços rodando:"
	@echo "    Dentist → http://localhost:8001/docs"
	@echo "    Lawyer  → http://localhost:8002/docs"

stop-all: stop-dentist stop-lawyer infra-down
	@echo "✔ Todos os serviços e infra parados."

# ── Docker (testes) ───────────────────────────────────────────────
test-env:
	docker compose -f $(INFRA)/docker-compose.test.yml -p $(COMPOSE_TEST_NAME) up -d --wait

test-env-down:
	docker compose -f $(INFRA)/docker-compose.test.yml -p $(COMPOSE_TEST_NAME) down -v

# ── Testes ────────────────────────────────────────────────────────
test-unit:
	python -m pytest tests/unit/ -v

test-integration: test-env
	python -m pytest tests/integration/ -v; \
	$(MAKE) test-env-down

test-dentist: test-env
	python -m pytest tests/unit/test_services/test_dentist/ tests/integration/test_services/test_dentist/ -v; \
	$(MAKE) test-env-down

test-lawyer: test-env
	python -m pytest tests/unit/test_services/test_lawyer/ tests/integration/test_services/test_lawyer/ -v; \
	$(MAKE) test-env-down

test-all: test-env
	python -m pytest tests/ -v; \
	$(MAKE) test-env-down

test-cov: test-env
	python -m pytest tests/ -v --cov=shared_core --cov=services --cov=infra --cov=messagebus --cov-report=term-missing; \
	$(MAKE) test-env-down

# ── Limpeza ───────────────────────────────────────────────────────
docker-clean:
	docker system prune -f

# ── Help ──────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  Infraestrutura"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make infra-up          → Sobe Postgres compartilhado (:54322)"
	@echo "  make infra-down        → Para Postgres (preserva dados)"
	@echo "  make infra-destroy     → Para Postgres e remove volumes"
	@echo ""
	@echo "  Deploy (Docker) — cada serviço sobe infra automaticamente"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make deploy-dentist    → Dentist API      http://localhost:8001/docs"
	@echo "  make deploy-lawyer     → Lawyer API       http://localhost:8002/docs"
	@echo "  make deploy-all        → Todos os serviços"
	@echo ""
	@echo "  Parar serviços"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make stop-dentist      → Para Dentist"
	@echo "  make stop-lawyer       → Para Lawyer"
	@echo "  make stop-all          → Para tudo (serviços + infra)"
	@echo ""
	@echo "  Logs"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make logs-dentist      → Logs do Dentist"
	@echo "  make logs-lawyer       → Logs do Lawyer"
	@echo "  make infra-logs        → Logs do Postgres"
	@echo ""
	@echo "  Testes"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make test-env          → Iniciar ambiente de testes"
	@echo "  make test-env-down     → Encerrar ambiente de testes"
	@echo "  make test-unit         → Testes unitários"
	@echo "  make test-integration  → Testes de integração"
	@echo "  make test-dentist      → Testes do dentista"
	@echo "  make test-lawyer       → Testes do advogado"
	@echo "  make test-all          → Todos os testes"
	@echo "  make test-cov          → Testes com cobertura"
	@echo ""
	@echo "  Qualidade"
	@echo "  ──────────────────────────────────────────────────"
	@echo "  make ruff              → Formata e corrige lint"
	@echo "  make lint              → Verifica lint"
	@echo "  make check             → Lint + type-check"
	@echo ""
