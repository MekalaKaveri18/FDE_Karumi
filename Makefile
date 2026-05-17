.PHONY: help install dev test lint format clean build docker-build docker-up docker-down run-validator run-tests run-dashboard run-api examples docs

help:
	@echo "Karumi Toolkit - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install              Install dependencies"
	@echo "  make dev                  Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  make test                 Run test suite"
	@echo "  make test-verbose         Run tests with verbose output"
	@echo "  make lint                 Run code linting"
	@echo "  make format               Format code with black"
	@echo "  make clean                Clean build artifacts"
	@echo ""
	@echo "Running:"
	@echo "  make run-validator        Run configuration validator"
	@echo "  make run-tests            Run example tests"
	@echo "  make run-dashboard        Run Streamlit dashboard"
	@echo "  make run-api              Run FastAPI server"
	@echo "  make examples             Run all examples"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-up            Start Docker containers"
	@echo "  make docker-down          Stop Docker containers"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs                 Build documentation"

install:
	pip install -r requirements.txt
	playwright install

dev:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt && pip install pytest black flake8
	playwright install

test:
	pytest tests/ -v --tb=short

test-verbose:
	pytest tests/ -vv --tb=long

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ examples/ --max-line-length=100 --exclude=__pycache__

format:
	black src/ tests/ examples/ --line-length=100

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .coverage -exec rm -r {} +
	find . -type d -name htmlcov -exec rm -r {} +
	rm -rf build/ dist/ *.egg-info

build:
	python setup.py sdist bdist_wheel

run-validator:
	python examples/example_1_onboarding_flow.py

run-tests:
	python examples/example_2_e2e_testing.py

run-monitoring:
	python examples/example_3_monitoring.py

run-dashboard:
	streamlit run src/monitoring/dashboard.py

run-api:
	python -m uvicorn src.monitoring.api:app --host 0.0.0.0 --port 8000 --reload

examples:
	@echo "Running Example 1: Onboarding Flow..."
	python examples/example_1_onboarding_flow.py
	@echo "\nRunning Example 2: E2E Testing..."
	python examples/example_2_e2e_testing.py
	@echo "\nRunning Example 3: Monitoring..."
	python examples/example_3_monitoring.py

docker-build:
	docker build -f docker/Dockerfile -t karumi-toolkit:latest .

docker-build-dev:
	docker build -f docker/Dockerfile.dev -t karumi-toolkit:dev .

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

docker-clean:
	docker-compose -f docker/docker-compose.yml down -v

docs:
	@echo "Documentation files:"
	@echo "  - README.md               Main documentation"
	@echo "  - PROJECT_STRUCTURE.md   Project structure guide"
	@echo "  - CONTRIBUTING.md        Contributing guidelines"

setup-env:
	cp .env.example .env
	@echo "Created .env file. Please update with your API keys."

all: clean install test
