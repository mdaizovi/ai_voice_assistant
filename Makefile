SERVER_PORT=8054
ifneq (,$(wildcard ./.dev.env))
	include .env
	export
endif


install:
	poetry install

setup: 
	install
	pre-commit install

run:
	cd src && poetry run uvicorn app.main:app --reload --port ${SERVER_PORT}