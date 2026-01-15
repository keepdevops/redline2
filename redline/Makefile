# REDLINE Makefile for Docker operations

.PHONY: help build up down restart logs shell test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

build-no-cache: ## Build Docker images without cache
	docker-compose build --no-cache

up: ## Start all services
	docker-compose up -d

up-dev: ## Start services in development mode (with logs)
	docker-compose up

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop services and remove volumes
	docker-compose down -v

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-web: ## Show logs from web service
	docker-compose logs -f web

logs-celery: ## Show logs from celery worker
	docker-compose logs -f celery-worker

shell: ## Open shell in web container
	docker-compose exec web /bin/bash

shell-celery: ## Open shell in celery container
	docker-compose exec celery-worker /bin/bash

test: ## Run tests
	docker-compose exec web pytest

clean: ## Remove containers, volumes, and images
	docker-compose down -v --rmi all

ps: ## Show running containers
	docker-compose ps

health: ## Check health of services
	@echo "Checking service health..."
	@curl -f http://localhost:5000/health || echo "Web service not healthy"
	@docker-compose exec redis redis-cli ping || echo "Redis not healthy"
	@docker-compose exec postgres pg_isready -U redline || echo "Postgres not healthy"

init-db: ## Initialize database schema
	docker-compose exec postgres psql -U redline -d redline -f /docker-entrypoint-initdb.d/01-schema.sql

migrate: ## Run database migrations (if needed)
	docker-compose exec web python -m database.migration_utils

prod-build: ## Build for production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Start in production mode
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
