lint:
	uv run ruff check --fix

format:
	uv run ruff format

migration:
	uv run python manage.py makemigrations src

migrate:
	uv run python manage.py migrate src

truncate_db:
	uv run python manage.py truncate_data --noinput

run:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	uv run python manage.py runserver $$SERVER_HOST:$$SERVER_PORT