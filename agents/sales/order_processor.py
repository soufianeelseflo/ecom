from utils.db import engine, Product, Order
from utils.logger import logger
from sqlmodel import Session, select
import requests
import os

class OrderProcessor:
    def __init__(self):
        """Initialize with COD Network seller token."""
        self.cod_token = os.getenv("COD_API_TOKEN")
        self.cod_base_url = "https://api.cod.network/v1"
        if not self.cod_token:
            raise ValueError("Missing COD_API_TOKEN")

    def list_product_on_cod(self, product):
        """List product on COD Network."""
        headers = {"Authorization": f"Bearer {self.cod_token}", "Content-Type": "application/json"}
        payload = {
            "name": product.name,
            "price": product.price,
            "description": product.name,
            "stock": product.stock
        }
        resp = requests.post(f"{self.cod_base_url}/products", json=payload, headers=headers)
        if resp.status_code == 201:
            logger.info(f"Listed {product.name} on COD")
            return resp.json().get("product_id")
        logger.warning(f"Failed to list {product.name}: {resp.text}")
        return None

    def process_orders(self):
        """Process orders and sync with COD Network."""
        with Session(engine) as session:
            try:
                pending_orders = session.exec(select(Order).where(Order.status == "pending")).all()
                headers = {"Authorization": f"Bearer {self.cod_token}", "Content-Type": "application/json"}
                for order in pending_orders:
                    product = session.get(Product, order.product_id)
                    if product and product.stock >= order.quantity:
                        cod_product_id = self.list_product_on_cod(product)
                        if not cod_product_id:
                            continue
                        cod_payload = {
                            "product_id": cod_product_id,
                            "quantity": order.quantity,
                            "price": product.price,
                            "destination": "UAE"
                        }
                        resp = requests.post(f"{self.cod_base_url}/orders", json=cod_payload, headers=headers)
                        if resp.status_code == 201:
                            order.cod_order_id = resp.json().get("order_id")
                            product.stock -= order.quantity
                            product.sales_count += order.quantity
                            product.revenue += order.quantity * product.price
                            order.status = "completed"
                            logger.info(f"Pushed order {order.id} to COD: {order.cod_order_id}")
                        else:
                            order.status = "failed"
                            logger.warning(f"COD push failed: {resp.text}")
                        session.add(product)
                    else:
                        order.status = "out_of_stock"
                        logger.warning(f"Order {order.id} failed: Out of stock")
                    session.add(order)
                session.commit()
            except Exception as e:
                logger.error(f"Order processing failed: {e}")
                session.rollback()