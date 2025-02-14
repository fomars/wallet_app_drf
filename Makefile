.PHONY: install, restart, migrate, downgrade, makemigrations, run, test, isort-check, isort-fix, black-check, black-fix

-include .env
export

PYTHON = ./.venv/bin/python
PIP = ./.venv/bin/pip

install:
	$(PIP) install -r requirements.txt

restart:
	docker-compose down && docker-compose up -d

migrate:
	$(PYTHON) manage.py migrate wallet_app

makemigrations:
	$(PYTHON) manage.py makemigrations wallet_app

create_admin:
	$(PYTHON) manage.py createsuperuser --username admin --email admin@example.com

run:
	$(PYTHON) manage.py runserver

test:
	$(PYTHON) -m pytest --cov=wallet_app --cov=wallet_app_drf --cov-report=term -v -s

isort-check:
	$(PYTHON) -m isort -c . --skip .venv

isort-fix:
	$(PYTHON) -m isort . --skip .venv

flake8:
	$(PYTHON) -m flake8 --max-line-length 99 --exclude .venv,wallet_app/migrations

black-check:
	$(PYTHON) -m black --check . --exclude .venv wallet_app/migrations

black-fix:
	$(PYTHON) -m black . --exclude .venv wallet_app/migrations
