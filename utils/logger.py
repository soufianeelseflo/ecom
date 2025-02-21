import logging
import os

logging.basicConfig(
    filename=os.path.join("data", "logs", "ai_agency.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("ai_agency")