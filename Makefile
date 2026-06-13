.PHONY: install lint typecheck test migrate migrate-graph setup-qdrant run-api run-worker run-web seed-demo seed-graph ingest-demo eval-citations-v0 eval-pipeline eval-prompt-injection compare-rerankers train-relevance seed-partner weekly-fp-report e2e load-test langfuse-up terraform-validate up bootstrap embed-sources

PYTHON ?= python
PIP ?= pip

up:
	docker compose up -d postgres neo4j qdrant redis
	@echo "Waiting for Postgres..."
	@$(PYTHON) scripts/wait_for_services.py
	$(MAKE) migrate
	$(MAKE) migrate-graph
	$(MAKE) setup-qdrant
	$(MAKE) seed-demo
	$(MAKE) embed-sources
	@echo ""
	@echo "RegIntel is ready. Next steps:"
	@echo "  Terminal 1: make run-api"
	@echo "  Terminal 2: make run-web"
	@echo "  Open http://localhost:3000 — login admin@regintel.dev / RegIntel-Demo-2025!"

bootstrap: up
install:
	$(PIP) install -e ".[dev]"

install-ml:
	$(PIP) install -e ".[dev,ml]"

lint:
	ruff check services tests scripts
	black --check services tests scripts

typecheck:
	mypy services

test:
	pytest tests/unit -v

migrate:
	alembic -c services/api/alembic.ini upgrade head

migrate-graph:
	$(PYTHON) scripts/run_graph_migrations.py

setup-qdrant:
	$(PYTHON) services/retrieval/migrations/setup_collection.py

seed-graph:
	$(PYTHON) scripts/seed_graph.py

run-api:
	uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload

run-worker:
	$(PYTHON) -m services.agents.worker

run-web:
	cd web && npm run dev

compare-rerankers:
	$(PYTHON) scripts/compare_rerankers.py --persist

seed-partner:
	$(PYTHON) scripts/seed_partner.py --tenant-name "Design Partner" --admin-email partner@example.com --profile-json scripts/partner_profile.example.json

weekly-fp-report:
	$(PYTHON) scripts/weekly_fp_report.py

ingest-demo:
	$(PYTHON) scripts/ingest_sources.py --sources ecfr --parts 1 101

seed-demo:
	$(PYTHON) scripts/seed_demo.py

embed-sources:
	$(PYTHON) scripts/embed_sources.py --sources reference sec_edgar --sec-limit 5

eval-citations-v0:
	$(PYTHON) -m services.eval.citation_presence_v0

eval-pipeline:
	$(PYTHON) -m services.eval.entailment.harness --persist

eval-prompt-injection:
	$(PYTHON) -m services.eval.prompt_injection.eval

train-relevance:
	$(PYTHON) scripts/train_relevance_model.py

e2e:
	pytest tests/e2e -v

load-test:
	$(PYTHON) scripts/load_test.py --base-url http://localhost:8000 --profiles 100

langfuse-up:
	docker compose -f docker-compose.yml -f infra/langfuse/docker-compose.langfuse.yml up -d langfuse langfuse-db

terraform-validate:
	cd infra/terraform/environments/staging && terraform init -backend=false && terraform validate
	cd infra/terraform/environments/production && terraform init -backend=false && terraform validate
