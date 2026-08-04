# Developer entrypoints. `make help` lists everything.
.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build all images
	$(COMPOSE) build

.PHONY: up
up: ## Start the full stack (dev)
	$(COMPOSE) up

.PHONY: down
down: ## Stop the stack
	$(COMPOSE) down

.PHONY: migrate
migrate: ## Apply DB migrations
	$(COMPOSE) run --rm backend python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Create new migrations
	$(COMPOSE) run --rm backend python manage.py makemigrations

.PHONY: superuser
superuser: ## Create a Django admin user
	$(COMPOSE) run --rm backend python manage.py createsuperuser

.PHONY: test
test: ## Run backend tests with coverage
	$(COMPOSE) run --rm backend pytest

.PHONY: lint
lint: ## Run all linters
	$(COMPOSE) run --rm backend sh -c "black --check . && isort --check-only . && flake8 . && mypy ."

.PHONY: fmt
fmt: ## Auto-format backend code
	$(COMPOSE) run --rm backend sh -c "black . && isort ."

.PHONY: e2e
e2e: ## Run Selenium end-to-end tests
	$(COMPOSE) -f docker-compose.yml -f docker-compose.e2e.yml run --rm e2e
