import logging

# Logging settings
format_log = (
    "\n# %(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s: \n%(message)s"
)
logging.basicConfig(
    level=logging.INFO,
    format=format_log,
)
log = logging.getLogger("TESTS_AI_ASSISTANT_API_LOG")
