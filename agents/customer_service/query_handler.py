from utils.api_router import APIRouter
from utils.logger import logger

class QueryHandler:
    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    def handle_query(self, query):
        try:
            prompt = f"Respond to this customer query politely and helpfully: '{query}'"
            response = self.api_router.generate(prompt)
            logger.info(f"Handled query: {query}")
            return response if response else "Thank you for your query! How can I assist you?"
        except Exception as e:
            logger.error(f"Query handling failed: {e}")
            return "Sorry, something went wrong. Please try again."