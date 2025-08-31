.PHONY: dev build fmt lint test migrate seed clean

# Development
dev:
	docker compose up

dev-build:
	docker compose up --build

# Build images
build:
	docker compose build

# Formatting
fmt:
	# Backend
	cd backend && \
		black . && \
		isort . && \
		ruff --fix .
	# Frontend
	cd frontend && \
		npm run format

# Linting
lint:
	# Backend
	cd backend && \
		ruff check . && \
		mypy .
	# Frontend
	cd frontend && \
		npm run lint

# Testing
test:
	# Backend
	cd backend && \
		pytest
	# Frontend
	cd frontend && \
		npm run test

# Database migrations
migrate:
	cd backend && \
		alembic upgrade head

migrate-revision:
	cd backend && \
		alembic revision --autogenerate -m "$(message)"

# Seed demo data
seed:
	cd backend && \
		python scripts/seed.py

# Clean up
clean:
	# Remove temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	# Frontend
	rm -rf frontend/node_modules
	rm -rf frontend/.next
