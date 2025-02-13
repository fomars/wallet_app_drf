.PHONY: install, restart, migrate, makemigrations, run, test, isort-check, isort-fix, black-check, black-fix

-include .env
export

VENV_ACTIVATE = .venv/bin/activate

venv:
	. $(VENV_ACTIVATE)

install: venv
	pip install -r requirements.txt

restart:
	docker-compose down && docker-compose up -d

migrate: venv
	python manage.py migrate

makemigrations: venv
	python manage.py makemigrations

create_admin: venv
	python manage.py createsuperuser --username admin --email admin@example.com

run: venv
	python manage.py runserver

test: venv
	python -m pytest -v -s

isort-check:
	python -m isort -c . --skip .venv

isort-fix:
	python -m isort . --skip .venv

flake8:
	python -m flake8 --max-line-length 99 --exclude .venv,wallet_app/migrations

black-check:
	python -m black --check . --exclude .venv wallet_app/migrations

black-fix:
	python -m black . --exclude .venv wallet_app/migrations