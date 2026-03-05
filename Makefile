.PHONY: dev build stop logs lint

dev:
	docker compose up --build

build:
	docker compose build

stop:
	docker compose down

logs:
	docker compose logs -f

lint:
	docker compose exec app python -m pip install ruff
	docker compose exec app ruff app