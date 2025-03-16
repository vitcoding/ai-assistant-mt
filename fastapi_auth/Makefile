# http://localhost:8001/api/openapi


# Service
up:
	docker compose -f docker-compose-auth.yml up -d --build --force-recreate
destroy:
	docker compose -f docker-compose-auth.yml down -v

# Tests
tests:
	docker compose -f src/tests/functional/docker-compose.yml up -d --build --force-recreate
tests-destroy:
	docker compose -f src/tests/functional/docker-compose.yml down -v
