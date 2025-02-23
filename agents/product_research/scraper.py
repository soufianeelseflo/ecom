from TikTokApi import TikTokApi
from utils.db import engine, Video, Comment
from utils.logger import logger
from sqlmodel import Session, select
import time

class TikTokScraper:
    def __init__(self):
        self.api = TikTokApi(custom_verify_fp="verify_fp_here")  # Replace with your fingerprint

    def scrape_trending(self, hashtags=["ecommerce", "ramadanproducts"], count=10):
        with Session(engine) as session:
            for hashtag in hashtags:
                try:
                    videos = self.api.hashtag(name=hashtag).videos(count=count)
                    for video in videos:
                        if not session.exec(select(Video).where(Video.id == video.id)).first():
                            session.add(Video(id=video.id, hashtag=hashtag, description=video.desc))
                            comments = video.comments(count=50)
                            for comment in comments:
                                if not session.exec(select(Comment).where(Comment.text == comment.text, Comment.video_id == video.id)).first():
                                    session.add(Comment(video_id=video.id, text=comment.text))
                            session.commit()
                        time.sleep(5)
                    logger.info(f"Scraped {count} videos for #{hashtag}")
                except Exception as e:
                    logger.error(f"Scraping failed: {e}")