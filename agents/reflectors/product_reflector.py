from utils.db import engine, Product
from utils.logger import logger
from sqlmodel import Session, select
from collections import Counter

class ProductReflector:
    def reflect(self):
        with Session(engine) as session:
            try:
                products = session.exec(select(Product).where(Product.sales_count > 0)).all()
                if not products:
                    logger.info("No sales data")
                    return {}
                top_products = sorted(products, key=lambda p: p.revenue, reverse=True)[:5]
                winners = {p.name: p.revenue for p in top_products}
                logger.info(f"Top products: {winners}")
                return winners
            except Exception as e:
                logger.error(f"Reflection failed: {e}")
                return {}