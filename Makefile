# Containers ids
postgres-id=$(shell docker ps -a -q -f "name=dinero-postgres")
django-id=$(shell docker ps -a -q -f "name=dinero-django")

# Build docker containers
build: build-django build-postgres
build-django:
	@docker-compose -f docker-compose.yml build dinero-django

build-postgres:
	@docker-compose -f docker-compose.yml build dinero-postgres

# Stop docker containers
stop-all:
	@docker-compose stop
stop-postgres:
	-@docker stop $(postgres-id)
stop-django:
	-@docker stop $(django-id)


# Remove docker containers
rm-all: rm-django rm-postgres
rm-postgres:
	-@docker rm $(postgres-id)
rm-django:
	-@docker rm $(django-id)

# Remove, build and run docker containers
rm-build: stop-all rm-all build run
rm-build-postgres: stop-postgres rm-postgres build-postgres
rm-build-django: stop-django rm-django build-django

# Run docker containers
run:
	@docker-compose -f docker-compose.yml up

run-django:
	@docker-compose -f docker-compose.yml up dinero-django


# Go to container ash shell
shell-django:
	@docker exec -it dinero-django ash

shell-postgres:
	@docker exec -it dinero-postgres ash


# Django commands
manage:
	@docker exec -t dinero-django python src/manage.py $(cmd)

migrate:
	@docker exec -t dinero-django python src/manage.py migrate

migrations:
	@docker exec -it dinero-django python src/manage.py makemigrations

migrations-empty:
	@docker exec -it dinero-django python src/manage.py makemigrations --empty $(app)

superuser:
	@docker exec -it dinero-django python src/manage.py createsuperuser

messages:
	@docker exec -it dinero-django python src/manage.py makemessages -l pl

compilemessages:
	@docker exec -it dinero-django python src/manage.py compilemessages

populatedb:
	@docker exec -it dinero-django python src/manage.py loaddata campaigns users

# Tests
test:
	@docker exec -t dinero-django /bin/sh -c "cd src && PYTHONDONTWRITEBYTECODE=1 python -m pytest $(dir) --disable-warnings"
