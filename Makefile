# Makefile

.PHONY: up down logs

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

rebuild:
	docker compose down --rmi all --volumes --remove-orphans
	docker compose up -d --build