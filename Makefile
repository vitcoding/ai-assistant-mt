# auth service api
# http://localhost:8001/api/openapi
# search service (movie theatre service) api
# http://localhost:8000/api/openapi


# auth
AUTH-DC = fastapi_auth/docker-compose-auth.yml
AUTH-NAME = auth
AUTH-SERVICE-NAME = auth-service
# search (movie theatre)
MT-DC = fastapi_movietheatre/docker-compose-mt.service-pg.yml
MT-NAME = mt
MT-SERVICE-NAME = mt-search-service


# network
net-create:
	docker network create shared-network
net-rm:
	docker network rm shared-network

# all services
up:
	make net-create
	make up-$(AUTH-NAME)
	make up-$(MT-NAME)
destroy:
	make destroy-$(MT-NAME)
	make destroy-$(AUTH-NAME)
	make net-rm
stop:
	make stop-$(MT-NAME)
	make stop-$(AUTH-NAME)
start:
	make start-$(AUTH-NAME)
	make start-$(MT-NAME)


# auth service
# AUTH-NAME = auth
up-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) up -d --build --force-recreate
destroy-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) down -v
rebuild-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) stop $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) rm -f $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) build $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) up -d $(AUTH-SERVICE-NAME)

stop-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) stop
start-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) start

tests-$(AUTH-NAME):
	make net-create
	docker compose -f fastapi_auth/src/tests/functional/docker-compose.yml up -d --build --force-recreate
	docker logs -f tests
	docker compose -f fastapi_auth/src/tests/functional/docker-compose.yml down -v
	make net-rm


# search service (movie theatre service)
# MT-NAME = mt
up-$(MT-NAME):
	docker compose -f $(MT-DC) up -d --build --force-recreate
destroy-$(MT-NAME):
	docker compose -f $(MT-DC) down -v
rebuild-$(MT-NAME):
	docker compose -f $(MT-DC) stop $(MT-SERVICE-NAME)
	docker compose -f $(MT-DC) rm -f $(MT-SERVICE-NAME)
	docker compose -f $(MT-DC) build $(MT-SERVICE-NAME)
	docker compose -f $(MT-DC) up -d $(MT-SERVICE-NAME)

stop-$(MT-NAME):
	docker compose -f $(MT-DC) stop
start-$(MT-NAME):
	docker compose -f $(MT-DC) start

tests-$(MT-NAME):
	make net-create
	docker compose -f fastapi_movietheatre/fastapi-solution/tests/functional/docker-compose.yml up -d --build --force-recreate
	docker logs -f tests
	docker compose -f fastapi_movietheatre/fastapi-solution/tests/functional/docker-compose.yml down -v
	make net-rm



# open project (vs code)
auth-prj:
	code fastapi_auth/src
mt-prj:
	code fastapi_movietheatre/fastapi-solution/src
ai-prj:
	code fastapi_ai_assistant/src


# other
dc-prune:
	docker system prune -a -f