# ================================================================================================
# NOWHERE.AI Platform - Makefile
# ================================================================================================
# Easy command execution for common tasks

.PHONY: help install start stop restart logs test lint clean backup restore verify build deploy

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(GREEN)NOWHERE.AI Platform - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ================================================================================================
# Installation & Setup
# ================================================================================================

install: ## Install all dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
	@cd frontend && yarn install
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

install-backend: ## Install backend dependencies only
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
	@echo "$(GREEN)✅ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies only
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	@cd frontend && yarn install
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

setup: ## Initial setup (copy env files, install deps)
	@echo "$(GREEN)Setting up project...$(NC)"
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@cp -n frontend/.env.example frontend/.env 2>/dev/null || true
	@make install
	@mkdir -p logs backups
	@echo "$(GREEN)✅ Setup complete$(NC)"

# ================================================================================================
# Service Management
# ================================================================================================

start: ## Start all services
	@./scripts/start.sh

stop: ## Stop all services
	@./scripts/stop.sh

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	@make stop
	@sleep 2
	@make start

start-docker: ## Start services with Docker Compose
	@echo "$(GREEN)Starting with Docker Compose...$(NC)"
	@docker-compose up -d
	@docker-compose ps

stop-docker: ## Stop Docker Compose services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	@docker-compose down

restart-docker: ## Restart Docker Compose services
	@docker-compose restart

# ================================================================================================
# Development
# ================================================================================================

dev: ## Start development servers
	@echo "$(GREEN)Starting development mode...$(NC)"
	@make -j 2 dev-backend dev-frontend

dev-backend: ## Start backend in development mode
	@cd backend && uvicorn server:app --reload --host 0.0.0.0 --port 8001

dev-frontend: ## Start frontend in development mode
	@cd frontend && yarn start

# ================================================================================================
# Testing
# ================================================================================================

test: ## Run all tests
	@echo "$(GREEN)Running all tests...$(NC)"
	@make test-backend
	@make test-frontend

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	@cd backend && pytest tests/ -v --cov=. --cov-report=term-missing

test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	@cd frontend && yarn test --watchAll=false --coverage

test-watch: ## Run tests in watch mode
	@cd backend && pytest tests/ -v --watch

# ================================================================================================
# Linting & Code Quality
# ================================================================================================

lint: ## Run linters on all code
	@make lint-backend
	@make lint-frontend

lint-backend: ## Lint backend code
	@echo "$(GREEN)Linting backend...$(NC)"
	@cd backend && black --check . || true
	@cd backend && pylint server.py --disable=all --enable=E,W || true

lint-frontend: ## Lint frontend code
	@echo "$(GREEN)Linting frontend...$(NC)"
	@cd frontend && yarn lint || true

format: ## Format all code
	@echo "$(GREEN)Formatting code...$(NC)"
	@cd backend && black .
	@cd frontend && yarn format || true
	@echo "$(GREEN)✅ Code formatted$(NC)"

# ================================================================================================
# Database
# ================================================================================================

db-indexes: ## Create database indexes
	@echo "$(GREEN)Creating database indexes...$(NC)"
	@cd backend && python database_indexes.py
	@echo "$(GREEN)✅ Indexes created$(NC)"

backup: ## Create database backup
	@./scripts/backup.sh

restore: ## Restore database from backup (usage: make restore BACKUP=path/to/backup.tar.gz)
	@./scripts/restore.sh $(BACKUP)

# ================================================================================================
# Logs
# ================================================================================================

logs: ## View all logs
	@tail -f logs/*.log 2>/dev/null || tail -f /var/log/supervisor/*.log

logs-backend: ## View backend logs
	@tail -f /var/log/supervisor/backend.*.log

logs-frontend: ## View frontend logs
	@tail -f /var/log/supervisor/frontend.*.log

logs-error: ## View error logs only
	@tail -f logs/*.error.log 2>/dev/null || tail -f /var/log/supervisor/*.err.log

# ================================================================================================
# Verification & Health
# ================================================================================================

verify: ## Verify production readiness
	@./scripts/verify-production.sh

health: ## Check system health
	@echo "$(GREEN)Checking system health...$(NC)"
	@curl -s http://localhost:8001/api/health | python3 -m json.tool || echo "Backend not responding"

health-detailed: ## Check detailed system health
	@echo "$(GREEN)Checking detailed system health...$(NC)"
	@curl -s "http://localhost:8001/api/health?detailed=true" | python3 -m json.tool

metrics: ## View application metrics
	@curl -s http://localhost:8001/api/metrics | python3 -m json.tool || echo "Metrics endpoint not available"

# ================================================================================================
# Build & Deploy
# ================================================================================================

build: ## Build for production
	@echo "$(GREEN)Building for production...$(NC)"
	@cd frontend && yarn build
	@echo "$(GREEN)✅ Build complete$(NC)"

build-docker: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	@docker-compose build

deploy-docker: ## Deploy with Docker Compose
	@echo "$(GREEN)Deploying with Docker...$(NC)"
	@docker-compose up -d --build
	@docker-compose ps
	@echo "$(GREEN)✅ Deployed successfully$(NC)"

# ================================================================================================
# Cleanup
# ================================================================================================

clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf frontend/build frontend/.cache
	@rm -rf backend/.pytest_cache backend/.coverage
	@echo "$(GREEN)✅ Cleaned$(NC)"

clean-all: clean ## Clean everything including dependencies
	@echo "$(YELLOW)Removing dependencies...$(NC)"
	@rm -rf frontend/node_modules
	@rm -rf backend/venv
	@echo "$(GREEN)✅ All cleaned$(NC)"

# ================================================================================================
# Docker Specific
# ================================================================================================

docker-logs: ## View Docker container logs
	@docker-compose logs -f

docker-ps: ## Show Docker container status
	@docker-compose ps

docker-exec-backend: ## Execute shell in backend container
	@docker-compose exec backend /bin/bash

docker-exec-frontend: ## Execute shell in frontend container
	@docker-compose exec frontend /bin/sh

# ================================================================================================
# Development Helpers
# ================================================================================================

shell-backend: ## Open Python shell with backend context
	@cd backend && python3 -i -c "from server import *; from database import *"

shell-db: ## Open MongoDB shell
	@mongo nowhereai

install-dev: ## Install development tools
	@pip install pytest pytest-cov pytest-asyncio black pylint
	@echo "$(GREEN)✅ Development tools installed$(NC)"

# ================================================================================================
# CI/CD
# ================================================================================================

ci-test: ## Run CI tests
	@echo "$(GREEN)Running CI tests...$(NC)"
	@make test
	@make lint
	@make verify

# ================================================================================================
# Status & Info
# ================================================================================================

status: ## Show system status
	@echo "$(GREEN)=== System Status ===$(NC)"
	@echo ""
	@echo "Services:"
	@sudo supervisorctl status 2>/dev/null || docker-compose ps 2>/dev/null || echo "No service manager found"
	@echo ""
	@echo "Ports:"
	@netstat -tuln 2>/dev/null | grep -E ":(8001|3000|27017)" || echo "Port information not available"
	@echo ""
	@make health

info: ## Show project information
	@echo "$(GREEN)=== NOWHERE.AI Platform Information ===$(NC)"
	@echo ""
	@echo "Version: 2.0.0"
	@echo "Backend: FastAPI + Python 3.11"
	@echo "Frontend: React 18"
	@echo "Database: MongoDB"
	@echo ""
	@echo "URLs:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8001"
	@echo "  API Docs: http://localhost:8001/docs"
	@echo ""
