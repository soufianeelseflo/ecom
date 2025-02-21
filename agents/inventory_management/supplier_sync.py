from utils.db import engine, Product
from utils.logger import logger
from sqlmodel import Session, select

class SupplierSync:
    def sync_inventory(self):
        with Session(engine) as session:
            try:
                products = session.exec(select(Product)).all()
                for product in products:
                    if product.stock < 5:
                        product.stock += 20  # Simulate restocking
                        session.add(product)
                        logger.info(f"Restocked {product.name} to {product.stock}")
                session.commit()
            except Exception as e:
                logger.error(f"Inventory sync failed: {e}")
                session.rollback()