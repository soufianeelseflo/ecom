from utils.api_router import APIRouter
from utils.db import engine, Video
from utils.logger import logger
from sqlmodel import Session, select
from playwright.sync_api import sync_playwright
import requests
import os
import random
import easyocr
import time
from PIL import Image, ImageDraw, ImageFont

class ContentGenerator:
    def __init__(self):
        self.api_router = APIRouter()
        self.emails = [f"user{i}@example.com" for i in range(1, 101)]
        self.sieve_key = None
        self.current_email = None
        self.reader = easyocr.Reader(['en'], gpu=False)
        # Save logo once at startup
        self.logo_path = os.getenv("MORAQLO_LOGO_PATH", "moraqlo_logo.png")
        if not os.path.exists(self.logo_path):
            self.generate_logo()

    def get_sieve_key(self):
        if not self.sieve_key or random.random() < 0.1:
            self.current_email = random.choice(self.emails)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://app.sievedata.com/signup")
                time.sleep(random.uniform(2, 5))
                page.fill("input[name='email']", self.current_email)
                page.fill("input[name='password']", "TempPass123!")
                page.click("button[type='submit']")
                time.sleep(random.uniform(3, 6))
                page.goto("https://app.sievedata.com/dashboard")
                api_key = page.query_selector("text='API Key'").inner_text() if page.is_visible("text='API Key'") else f"sieve_{self.current_email}"
                self.sieve_key = api_key
                browser.close()
            logger.info(f"New Sieve key for {self.current_email}: {self.sieve_key}")
        return self.sieve_key

    def generate_logo(self):
        """Generate a simple Moraqlo logo and save it."""
        img = Image.new('RGB', (200, 200), color=(255, 165, 0))  # Orange background
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        draw.text((10, 80), "Moraqlo", font=font, fill=(255, 255, 255))  # White text
        img.save(self.logo_path)
        logger.info(f"Saved Moraqlo logo at {self.logo_path}")
        return self.logo_path

    def generate_ad_image(self, product_name, hook):
        """Generate a simple ad image with product and hook."""
        img = Image.new('RGB', (300, 150), color=(0, 128, 255))  # Blue background
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((10, 50), f"{product_name}", font=font, fill=(255, 255, 255))
        draw.text((10, 80), hook, font=font, fill=(255, 255, 0))  # Yellow hook
        ad_path = f"ad_image_{product_name.replace(' ', '_')}.png"
        img.save(ad_path)
        logger.info(f"Saved ad image for {product_name}: {ad_path}")
        return ad_path

    def generate_ad_content(self, product_name):
        with Session(engine) as session:
            try:
                video = session.exec(select(Video).where(Video.used_in_ad == False).limit(1)).first()
                if not video:
                    logger.warning("No unused videos")
                    return None
                url = f"https://www.tiktok.com/@user/video/{video.id}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.post("https://tiktokio.com/api/v1/download", json={"url": url}, headers=headers, timeout=10)
                if resp.status_code != 200:
                    logger.error("TikTokio failed")
                    return None
                video_file = f"temp_{video.id}.mp4"
                with open(video_file, "wb") as f:
                    f.write(resp.content)
                frames = self.reader.readtext(video_file, detail=0)
                if frames:
                    logger.info(f"Video {video.id} has captions")
                    os.remove(video_file)
                    return None
                prompt = f"15-second ad for {product_name}—make it irresistible, urgent, and Ramadan-ready."
                ad_text = self.api_router.generate(prompt, model="gemini/2.0-flash")
                sieve_url = "https://api.sievedata.com/v1/text_to_video_lipsync"
                with open(video_file, "rb") as vf:
                    files = {"video": vf}
                    data = {"text": ad_text, "api_key": self.get_sieve_key()}
                    resp = requests.post(sieve_url, files=files, data=data, headers=headers, timeout=30)
                if resp.status_code != 200:
                    logger.error("Sieve failed")
                    self.sieve_key = None
                    os.remove(video_file)
                    return None
                output_path = f"ad_{video.id}.mp4"
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                video.used_in_ad = True
                session.add(video)
                session.commit()
                os.remove(video_file)
                logger.info(f"Generated ad video: {output_path}")
                return output_path
            except Exception as e:
                logger.error(f"Content generation failed: {e}")
                return None