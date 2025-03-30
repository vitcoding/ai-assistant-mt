import logging
import os

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}


log = logging.getLogger("DEBUG_LOG")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "\n# %(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s: \n%(message)s"
)

file_path_info = f"./_temp/logs/main_info.log"
file_path_debug = f"./_temp/logs/main_debug.log"
for file_path in (file_path_info, file_path_debug):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if file_path.endswith("_info.log"):
        file_handler_info = logging.FileHandler(
            filename=file_path, mode="a", encoding="utf-8"
        )
        file_handler_info.setLevel(logging.INFO)
        file_handler_info.setFormatter(formatter)
        log.addHandler(file_handler_info)
    elif file_path.endswith("_debug.log"):
        file_handler_debug = logging.FileHandler(
            filename=file_path, mode="a", encoding="utf-8"
        )
        file_handler_debug.setLevel(logging.DEBUG)
        file_handler_debug.setFormatter(formatter)
        log.addHandler(file_handler_debug)
