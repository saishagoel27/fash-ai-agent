import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # prints logs to console
    ]
)

# Reusable logger
logger = logging.getLogger("gssoc25_project")
