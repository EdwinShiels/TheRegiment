.PHONY: install lint test build-ui build-api build build-images push-images clean

# Variables
PYTHON := python3
POETRY := poetry
NPM := npm
DOCKER_REGISTRY := myrepo
VERSION := latest

# Installation
install:
	@echo "Installing Python dependencies..."
	$(POETRY) install
	@echo "Installing UI dependencies..."
	cd battle-station-ui && $(NPM) install

# Linting
lint:
	@echo "Running Python linters..."
	$(POETRY) run black api/
	$(POETRY) run isort api/
	$(POETRY) run flake8 api/
	$(POETRY) run mypy api/
	@echo "Running UI linters..."
	cd battle-station-ui && $(NPM) run lint

# Testing
test:
	@echo "Running Python tests..."
	$(POETRY) run pytest api/tests/
	@echo "Running UI tests..."
	cd battle-station-ui && $(NPM) run test

# Building
build-ui:
	@echo "Building UI..."
	cd battle-station-ui && $(NPM) run build

build-api:
	@echo "Building API..."
	$(POETRY) build

# Docker image building
build-images:
	@echo "Building Docker images..."
	docker build -f docker/engines/onboarding/Dockerfile -t $(DOCKER_REGISTRY)/onboarding:$(VERSION) docker/engines/onboarding
	docker build -f docker/engines/meal_delivery/Dockerfile -t $(DOCKER_REGISTRY)/meal-delivery:$(VERSION) docker/engines/meal_delivery
	docker build -f docker/engines/training/Dockerfile -t $(DOCKER_REGISTRY)/training:$(VERSION) docker/engines/training
	docker build -f docker/engines/cardio/Dockerfile -t $(DOCKER_REGISTRY)/cardio:$(VERSION) docker/engines/cardio
	docker build -f docker/engines/checkin/Dockerfile -t $(DOCKER_REGISTRY)/checkin:$(VERSION) docker/engines/checkin
	docker build -f docker/engines/infraction/Dockerfile -t $(DOCKER_REGISTRY)/infraction:$(VERSION) docker/engines/infraction
	docker build -f docker/engines/dspy/Dockerfile -t $(DOCKER_REGISTRY)/dspy:$(VERSION) docker/engines/dspy
	docker build -f docker/engines/scheduler/Dockerfile -t $(DOCKER_REGISTRY)/scheduler:$(VERSION) docker/engines/scheduler
	docker build -f docker/ui/Dockerfile -t $(DOCKER_REGISTRY)/battle-station-ui:$(VERSION) battle-station-ui

# Push images to registry
push-images:
	@echo "Pushing Docker images..."
	docker push $(DOCKER_REGISTRY)/onboarding:$(VERSION)
	docker push $(DOCKER_REGISTRY)/meal-delivery:$(VERSION)
	docker push $(DOCKER_REGISTRY)/training:$(VERSION)
	docker push $(DOCKER_REGISTRY)/cardio:$(VERSION)
	docker push $(DOCKER_REGISTRY)/checkin:$(VERSION)
	docker push $(DOCKER_REGISTRY)/infraction:$(VERSION)
	docker push $(DOCKER_REGISTRY)/dspy:$(VERSION)
	docker push $(DOCKER_REGISTRY)/scheduler:$(VERSION)
	docker push $(DOCKER_REGISTRY)/battle-station-ui:$(VERSION)

# Full build
build: build-ui build-api build-images

# Development
dev:
	@echo "Starting development environment..."
	docker-compose up

# Cleanup
clean:
	@echo "Cleaning up..."
	rm -rf api/dist/
	rm -rf battle-station-ui/dist/
	rm -rf battle-station-ui/node_modules/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 