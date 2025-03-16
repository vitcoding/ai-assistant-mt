# Сервис ИИ Ассистент

## Описание.
В сервисе реализован чат с ИИ Ассистентом, который отвечает на вопросы и имеет возможность подкреплять ответы данными о фильмах на основе RAG (Retrieval Augmented Generation).

Более подробно сервис описан по [ссылке](fastapi_ai_assistant/README.md).

### Основные команды для запуска сервисов:

- **запуск сервисов в docker compose**: 
`make up`;
- **остановка сервисов**: 
`make destroy`;
- **тесты ai_assistant_api**:
`make tests-ai`.

Более подробно все основные команды представлены в [Makefile](Makefile).

По умолчанию при разворачивании ollama для экономии времени загружается модель 'gemma3:4b'. Для использования в чате других предопределенных моделей их необходимо установить дополнительно. 
