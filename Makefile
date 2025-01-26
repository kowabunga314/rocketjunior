# Makefile

.PHONY: init

init:
	./setup.sh

build:
	docker compose up -d --build

start:
	docker compose up -d

test:
	docker compose exec api python manage.py test

stop:
	docker compose stop

destroy:
	docker compose down -v
