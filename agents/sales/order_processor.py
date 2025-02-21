from utils.db import engine, Product, Order
from utils.logger import logger
from sqlmodel import Session, select

class OrderProcessor:
    def process_orders(self):
        with Session(engine) as session:
            try:
                pending_orders = session.exec(select(Order).where(Order.status == "pending")).all()
                for order in pending_orders:
                    product = session.get(Product, order.product_id)
                    if product and product.stock >= order.quantity:
                        product.stock -= order.quantity
                        order.status = "completed"
                        session.add(product)
                        session.add(order)
                        logger.info(f"Processed order {order.id} for {product.name}")
                    else:
                        order.status = "out_of_stock"
                        session.add(order)
                        logger.warning(f"Order {order.id} failed: Out of stock")
                session.commit()
            except Exception as e:
                logger.error(f"Order processing failed: {e}")
                session.rollback()