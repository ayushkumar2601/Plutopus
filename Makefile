.PHONY: dev lint test format clean seed-topology

# Spin up the entire infrastructure stack locally via Docker Compose
dev:
	docker compose up --build

# Run all linters (Ruff, Mypy, ESLint)
lint:
	@echo "=== Linting Python packages with Ruff ==="
	python3 -m ruff check apps/api apps/cli packages/schemas
	@echo "=== Type checking Python packages with Mypy ==="
	python3 -m mypy apps/api apps/cli packages/schemas
	@echo "=== Linting Dashboard with Next/ESLint ==="
	npm --prefix apps/dashboard run lint

# Format codebase (Black, Ruff, Prettier)
format:
	@echo "=== Formatting Python code with Black ==="
	python3 -m black apps/api apps/cli packages/schemas
	@echo "=== Formatting Python imports/code with Ruff ==="
	python3 -m ruff check --fix apps/api apps/cli packages/schemas
	@echo "=== Formatting Dashboard code ==="
	npm --prefix apps/dashboard exec -- npx prettier --write "src/**/*.{ts,tsx,css,json}"

# Run automated tests
test:
	@echo "=== Running Python tests ==="
	python3 -m pytest apps/api apps/cli packages/schemas

# Seed Lab Topology
seed-topology:
	@echo "=== Seeding Lab Topology ==="
	PYTHONPATH=packages/shared/src:services/topology python3 services/topology/seed.py
