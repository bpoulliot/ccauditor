.PHONY: dev build stop logs lint format test audit deps shell

dev:
	docker compose up --build

build:
	docker compose build

stop:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec app bash

lint:
	docker compose exec app ruff check app

format:
	docker compose exec app black app
	docker compose exec app isort app

test:
	docker compose exec app pytest

audit:
	docker compose exec app pip-audit

deps:
	docker compose exec app pip-compile requirements.in --output-file=requirements.txt

hooks:
	pre-commit install