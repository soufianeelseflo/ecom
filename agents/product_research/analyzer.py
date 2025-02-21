from utils.api_router import APIRouter
from utils.db import engine, Comment, Product, Video
from utils.logger import logger
from sqlmodel import Session, select

class CommentAnalyzer:
    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    def analyze_comments(self):
        with Session(engine) as session:
            try:
                unanalyzed = session.exec(select(Comment).where(Comment.analyzed == False)).all()
                for comment in unanalyzed:
                    prompt = f"Does this comment show purchase intent? '{comment.text}' (Answer 'yes' or 'no')"
                    intent = self.api_router.generate(prompt)
                    if intent and "yes" in intent.lower():
                        video = session.get(Video, comment.video_id)
                        if video:
                            product_name = self.extract_product_name(video.description)
                            if not session.exec(select(Product).where(Product.name == product_name)).first():
                                session.add(Product(
                                    name=product_name,
                                    cost=20.0,
                                    price=100.0,
                                    supplier_id="tiktok_supplier",
                                    stock=10
                                ))
                    comment.analyzed = True
                session.commit()
                logger.info(f"Analyzed {len(unanalyzed)} comments")
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                session.rollback()

    def extract_product_name(self, text):
        prompt = f"Extract the product name from: '{text}'"
        name = self.api_router.generate(prompt)
        return name.strip() if name else "Unknown Product"