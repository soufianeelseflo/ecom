import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("data/logs", exist_ok=True)
logger = logging.getLogger("ai_agency")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("data/logs/ai_agency.log", maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)