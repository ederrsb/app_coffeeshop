import logging
from logging.handlers import RotatingFileHandler
import os

logger = logging.getLogger(__name__)

def setup_logger():
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s] - %(message)s")

    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_coffeeshop.log')

    rotating_handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
    rotating_handler.setFormatter(log_formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(rotating_handler)

setup_logger()