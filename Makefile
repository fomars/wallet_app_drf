.PHONY: install, restart, migrate

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

create_admin: venv
	python manage.py createsuperuser --username admin --email admin@example.com

run: venv
	python manage.py runserver
