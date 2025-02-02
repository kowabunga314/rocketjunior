# Makefile

.PHONY: init

init:
	./setup.sh

build:
	docker compose up -d --build

start:
	docker compose up -d

test-be:
	docker compose exec api python manage.py test

test-fe:
	docker compose exec -e REACT_APP_API_URL=http://json-server:3001 fe yarn test

stop:
	docker compose stop

destroy:
	docker compose down -v
