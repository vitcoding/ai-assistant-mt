# ai assistant service api
# http://localhost:8005/api/v1/chat_ai/
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
# ai assistant service
AI-DC = fastapi_ai_assistant/docker-compose-ai.yml
AI-NAME = ai
AI-SERVICE-NAME = ai_assistant_api
# ai infrastructure (cpu)
AIINFRA-DC = ai_infrastructure/docker-compose-aiinfra.yml
AIINFRA-NAME = ollama
AIINFRA-SERVICE-NAME = ollama-ai
# ai infrastructure (intel gpu, debug)
AIINFRA-DC-INTEL-GPU = ai_infrastructure/docker-compose-aiinfra.gpu-debug.yml


# network
net-create:
	docker network create shared-network
net-rm:
	docker network rm shared-network

# all services
up:
	make net-create
	make up-$(AIINFRA-NAME)
	docker compose -f $(AIINFRA-DC) exec -it ollama-ai ollama pull evilfreelancer/enbeddrus
	docker compose -f $(AIINFRA-DC) exec -it ollama-ai ollama pull llama3.2:3b
	docker compose -f $(AIINFRA-DC) exec -it ollama-ai ollama pull gemma2:9b
	make up-$(AUTH-NAME)
	make up-$(MT-NAME)
	make up-$(AI-NAME)
destroy:
	make destroy-$(AI-NAME)
	make destroy-$(MT-NAME)
	make destroy-$(AUTH-NAME)
	make destroy-$(AIINFRA-NAME)
	make net-rm
stop:
	make stop-$(AI-NAME)
	make stop-$(MT-NAME)
	make stop-$(AUTH-NAME)
	make stop-$(AIINFRA-NAME)
start:
	make start-$(AIINFRA-NAME)
	make start-$(AUTH-NAME)
	make start-$(MT-NAME)
	make start-$(AI-NAME)


# ai assistant service
# AI-NAME = ai
up-$(AI-NAME):
	docker compose -f $(AI-DC) up -d --build --force-recreate
destroy-$(AI-NAME):
	docker compose -f $(AI-DC) down -v
rebuild-$(AI-NAME):
	docker compose -f $(AI-DC) stop $(AI-SERVICE-NAME)
	docker compose -f $(AI-DC) rm -f $(AI-SERVICE-NAME)
	docker compose -f $(AI-DC) build $(AI-SERVICE-NAME)
	docker compose -f $(AI-DC) up -d $(AI-SERVICE-NAME)
# docker logs -f $(AI-SERVICE-NAME)
rebuild-ai-nginx:
	docker compose -f $(AI-DC) stop ai_assistant-nginx
	docker compose -f $(AI-DC) rm -f ai_assistant-nginx
	docker compose -f $(AI-DC) build ai_assistant-nginx
	docker compose -f $(AI-DC) up -d ai_assistant-nginx

stop-$(AI-NAME):
	docker compose -f $(AI-DC) stop
start-$(AI-NAME):
	docker compose -f $(AI-DC) start

tests-$(AI-NAME):
	docker network create test-network
	docker compose -f fastapi_ai_assistant/src/tests/docker-compose.yml up -d --build --force-recreate
	docker logs -f tests
	docker compose -f fastapi_ai_assistant/src/tests/docker-compose.yml down -v
	docker network rm test-network
# docker compose -f fastapi_ai_assistant/src/tests/docker-compose.yml down --rmi all --volumes

# ai_infrastructure
# AIINFRA-NAME = ollama
up-$(AIINFRA-NAME):
	docker compose -f $(AIINFRA-DC) up -d --build --force-recreate
destroy-$(AIINFRA-NAME):
	docker compose -f $(AIINFRA-DC) down -v
rebuild-$(AIINFRA-NAME):
	docker compose -f $(AIINFRA-DC) stop $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DC) rm -f $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DC) build $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DC) up -d $(AIINFRA-SERVICE-NAME)
# docker logs -f $(AIINFRA-SERVICE-NAME)

stop-$(AIINFRA-NAME):
	docker compose -f $(AIINFRA-DC) stop
start-$(AIINFRA-NAME):
	docker compose -f $(AIINFRA-DC) start


# Ollama commands examples
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama pull llama3.2:3b
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama pull evilfreelancer/enbeddrus
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama pull gemma2:9b
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama pull gemma3:4b
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama pull gemma3:12b
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama run gemma3:4b
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama list
# docker compose -f ai_infrastructure/docker-compose-aiinfra.yml exec -it ollama-ai ollama rm gemma3:4b


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
rebuild-etl:
	docker compose -f $(MT-DC) stop mt-etl
	docker compose -f $(MT-DC) rm -f mt-etl
	docker compose -f $(MT-DC) build mt-etl
	docker compose -f $(MT-DC) up -d mt-etl

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
etl-prj:
	code fastapi_movietheatre/etl


# other
dc-prune:
	docker system prune -a -f
dc-volume-prune:
	docker volume prune -f


### ai assistant debug mode
# ai infrastructure
AIINFRA-DEBUG-DC = ai_infrastructure/docker-compose-aiinfra.debug.yml
AIINFRA-DEBUG-NAME = ollama-debug

# ai_infrastructure (debug)
# AIINFRA-DEBUG-DEBUG-NAME = ollama-debug
up-$(AIINFRA-DEBUG-NAME):
	docker compose -f $(AIINFRA-DEBUG-DC) up -d --build --force-recreate
destroy-$(AIINFRA-DEBUG-NAME):
	docker compose -f $(AIINFRA-DEBUG-DC) down -v
rebuild-$(AIINFRA-DEBUG-NAME):
	docker compose -f $(AIINFRA-DEBUG-DC) stop $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DEBUG-DC) rm -f $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DEBUG-DC) build $(AIINFRA-SERVICE-NAME)
	docker compose -f $(AIINFRA-DEBUG-DC) up -d $(AIINFRA-SERVICE-NAME)

stop-$(AIINFRA-DEBUG-NAME):
	docker compose -f $(AIINFRA-DEBUG-DC) stop
start-$(AIINFRA-DEBUG-NAME):
	docker compose -f $(AIINFRA-DEBUG-DC) start

# launch in debug mode (all services)
up-debug-all:
	make net-create
	make up-$(AIINFRA-DEBUG-NAME)
	make up-$(AUTH-NAME)
	make up-$(MT-NAME)
	make ai-prj
destroy-debug-all:
	make destroy-$(MT-NAME)
	make destroy-$(AUTH-NAME)
	make destroy-$(AIINFRA-DEBUG-NAME)
	make net-rm
stop-debug-all:
	make stop-$(MT-NAME)
	make stop-$(AUTH-NAME)
	make stop-$(AIINFRA-DEBUG-NAME)
start-debug-all:
	make start-$(AIINFRA-DEBUG-NAME)
	make start-$(AUTH-NAME)
	make start-$(MT-NAME)
	make ai-prj


# launch in debug mode (without search service)
up-debug:
	make net-create
	make up-$(AIINFRA-DEBUG-NAME)
	make up-$(AUTH-NAME)
	make ai-prj
destroy-debug:
	make destroy-$(AUTH-NAME)
	make destroy-$(AIINFRA-DEBUG-NAME)
	make net-rm
stop-debug:
	make stop-$(AUTH-NAME)
	make stop-$(AIINFRA-DEBUG-NAME)
start-debug:
	make start-$(AIINFRA-DEBUG-NAME)
	make start-$(AUTH-NAME)
	make ai-prj

# ollama intel gpu (debug)
up-ollama-igpu:
	docker compose -f $(AIINFRA-DC-INTEL-GPU) up -d --build --force-recreate
destroy-ollama-igpu:
	docker compose -f $(AIINFRA-DC-INTEL-GPU) down -v
	