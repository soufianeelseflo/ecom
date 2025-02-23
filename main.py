from apscheduler.schedulers.background import BackgroundScheduler
from agents.product_research.scraper import TikTokScraper
from agents.product_research.analyzer import CommentAnalyzer
from agents.inventory_management.supplier_sync import SupplierSync
from agents.marketing.content_generator import ContentGenerator
from agents.marketing.ad_manager import AdManager
from agents.customer_service.query_handler import QueryHandler
from agents.sales.order_processor import OrderProcessor
from agents.analytics.performance_analyzer import PerformanceAnalyzer
from utils.api_router import APIRouter
from utils.logger import logger

def main():
    """Run the full AI agency autonomously."""
    api_router = APIRouter()
    scraper = TikTokScraper()
    analyzer = CommentAnalyzer()
    supplier_sync = SupplierSync()  # Placeholder; code this if needed
    content_gen = ContentGenerator()
    ad_manager = AdManager(content_gen)
    query_handler = QueryHandler(api_router)  # Placeholder; code this if needed
    order_processor = OrderProcessor()  # Placeholder; code this if needed
    performance_analyzer = PerformanceAnalyzer()  # Placeholder; code this if needed

    scheduler = BackgroundScheduler()  # https://apscheduler.readthedocs.io/
    scheduler.add_job(scraper.scrape_trending, "cron", hour=0)
    scheduler.add_job(analyzer.analyze_comments, "cron", hour=1)
    scheduler.add_job(supplier_sync.sync_inventory, "cron", hour=2)
    scheduler.add_job(ad_manager.run_campaigns, "cron", hour=3)
    scheduler.add_job(order_processor.process_orders, "cron", hour=4)
    scheduler.add_job(performance_analyzer.analyze, "cron", hour=5)
    scheduler.start()

    logger.info("AI Agency started")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("AI Agency stopped")

if __name__ == "__main__":
    main()