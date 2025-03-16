# http://localhost:8000/api/openapi


# Service
up:
	docker compose -f docker-compose-mt.yml up -d --build --force-recreate
destroy:
	docker compose -f docker-compose-mt.yml down -v

# Tests
tests:
	docker compose -f fastapi-solution/tests/functional/docker-compose.yml up -d --build --force-recreate
tests-destroy:
	docker compose -f fastapi-solution/tests/functional/docker-compose.yml down -v
