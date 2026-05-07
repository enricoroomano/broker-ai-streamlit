import logging
from rich.logging import RichHandler

def setup_logger():
    # Configura un logger elegante per il terminale
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("insurance_assistant")
