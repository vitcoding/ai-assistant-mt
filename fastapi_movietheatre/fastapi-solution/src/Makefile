run:
	gunicorn -c gunicorn.conf.py main:app

debug:
	python -c "from core.logger import configure_logging, log; \
	configure_logging(); import uvicorn; \
	uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"