import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from api import router
from core.config import config
from core.logger import LOGGING

app = FastAPI(
    title=config.globals.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.mount("/static", StaticFiles(directory="api/v1/static"), name="static")


app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
