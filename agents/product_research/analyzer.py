from utils.api_router import APIRouter
from utils.db import engine, Comment, Product, Video
from utils.logger import logger
from sqlmodel import Session, select
from transformers import pipeline  # Docs: https://huggingface.co/docs/transformers
from content_generator import ContentGenerator
import requests
import time

class CommentAnalyzer:
    def __init__(self):
        self.api_router = APIRouter()
        self.grader = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", framework="pt")
        self.supplier_url = "https://api.cjdropshipping.com/v1/product/search"  # Docs: https://developers.cjdropshipping.com/
        self.supplier_token = os.getenv("CJ_API_KEY")
        self.content_gen = ContentGenerator()

    def analyze_convergence(self, comment_text):
        prompt = f"Does this comment show purchase intent or trend potential? 'Yes' or 'No': '{comment_text}'"
        intent = self.api_router.generate(prompt, model="gemini/2.0-flash")
        return "yes" in intent.lower() if intent else False

    def source_product(self, product_name):
        headers = {"Authorization": f"Bearer {self.supplier_token}", "Content-Type": "application/json"}
        resp = requests.get(self.supplier_url, params={"keyword": product_name}, headers=headers)
        if resp.status_code == 200 and resp.json().get("data"):
            product = resp.json()["data"][0]
            return {"name": product["productName"], "cost": product["costPrice"], "price": product["sellingPrice"], "id": product["productId"], "stock": product["stock"]}
        return None

    def analyze_comments(self):
        with Session(engine) as session:
            try:
                unanalyzed = session.exec(select(Comment).where(Comment.analyzed == False)).all()
                for comment in unanalyzed:
                    sentiment = self.grader(comment.text)[0]["label"]
                    comment.sentiment = sentiment
                    if sentiment == "POSITIVE" and self.analyze_convergence(comment.text):
                        video = session.get(Video, comment.video_id)
                        if video:
                            product_data = self.source_product(video.description)
                            if product_data:
                                existing = session.exec(select(Product).where(Product.name == product_data["name"])).first()
                                if not existing:
                                    image_path = self.content_gen.generate_ad_image(product_data["name"])
                                    session.add(Product(
                                        name=product_data["name"],
                                        cost=product_data["cost"],
                                        price=product_data["price"],
                                        supplier_id=product_data["id"],
                                        stock=product_data["stock"],
                                        image_path=image_path
                                    ))
                                    logger.info(f"Added trending {product_data['name']} with image: {image_path}")
                    comment.analyzed = True
                    session.add(comment)
                session.commit()
                logger.info(f"Analyzed {len(unanalyzed)} comments")
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                session.rollback()