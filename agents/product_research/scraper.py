import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from sqlalchemy.orm import Session
from utils.db import Product
import time

class ProductResearchAgent:
    def __init__(self, db_session: Session, api_router):
        self.db = db_session
        self.api_router = api_router
        self.ua = UserAgent()

    def scrape_trending(self):
        url = "https://www.amazon.com/s?k=ramadan+products"  # Example
        headers = {"User-Agent": self.ua.random}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        products = []
        for item in soup.select(".s-result-item")[:5]:  # Top 5 items
            name = item.select_one(".a-text-normal").text.strip()
            price = float(item.select_one(".a-price-whole").text.replace(",", ""))
            products.append({"name": name, "price": price})
        time.sleep(2)  # Anti-detection delay
        return products

    def analyze_products(self, products):
        for p in products:
            prompt = f"Evaluate this product for Ramadan sales: {p['name']}, price: ${p['price']}"
            analysis = self.api_router.request(prompt, "high")
            if "high potential" in analysis.lower():
                self.db.add(Product(name=p["name"], cost=p["price"] * 0.2, price=p["price"], supplier_id="drop1"))
        self.db.commit()