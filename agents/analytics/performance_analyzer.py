from utils.db import engine, Order
from utils.logger import logger
from sqlmodel import Session, select

class PerformanceAnalyzer:
    def analyze(self):
        with Session(engine) as session:
            try:
                completed_orders = session.exec(select(Order).where(Order.status == "completed")).all()
                revenue = sum(order.quantity * session.get(Product, order.product_id).price for order in completed_orders)
                logger.info(f"Total revenue: ${revenue:.2f}")
                if revenue < 1000:
                    logger.info("Suggestion: Increase ad budget or adjust pricing")
            except Exception as e:
                logger.error(f"Performance analysis failed: {e}")