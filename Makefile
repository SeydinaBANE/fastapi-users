.PHONY: install setup run test lint format typecheck check migrate docker-up docker-down

install:
	pip install -r requirements.txt

setup: install
	pre-commit install

run:
	uvicorn main:app --reload

test:
	pytest -v

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy . --ignore-missing-imports

check: lint typecheck
	ruff format --check .

migrate:
	alembic upgrade head

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
