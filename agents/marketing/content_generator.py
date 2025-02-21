from utils.api_router import APIRouter
from utils.logger import logger

class ContentGenerator:
    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    def generate_ad_content(self, product_name):
        try:
            prompt = f"Create a short, compelling ad for {product_name} targeting Ramadan shoppers."
            content = self.api_router.generate(prompt)
            if content:
                logger.info(f"Generated ad content for {product_name}")
                return content
            return "Default ad for " + product_name
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return None