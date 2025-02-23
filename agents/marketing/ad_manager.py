from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
from utils.db import engine, Product, AdCampaign
from utils.logger import logger
from sqlmodel import Session, select
import requests
import os
import time

class AdManager:
    def __init__(self, content_generator):
        self.fb_access_token = os.getenv("FB_ACCESS_TOKEN")
        self.fb_account_id = os.getenv("FB_ACCOUNT_ID")
        self.fb_adset_id = os.getenv("FB_ADSET_ID")
        self.fb_page_id = os.getenv("FB_PAGE_ID")
        self.store_link = os.getenv("STORE_LINK", "https://moraqlo.com")
        if not all([self.fb_access_token, self.fb_account_id, self.fb_adset_id, self.fb_page_id]):
            raise ValueError("Missing Facebook env vars")
        FacebookAdsApi.init(access_token=self.fb_access_token)  # Docs: https://developers.facebook.com/docs/marketing-api/sdks/
        self.content_generator = content_generator
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.daily_budget = 500  # $5/day per niche in cents (2025)

    def run_campaigns(self):
        """Test niche-specific products on Facebook, TikTokio, Sieve."""
        with Session(engine) as session:
            try:
                niches = {
                    "Tech Gadgets": ["gadget", "tech", "device"],
                    "Fashion Finds": ["fashion", "clothing", "accessory"],
                    "Home Essentials": ["home", "decor", "appliance"]
                }
                for niche_name, keywords in niches.items():
                    products = session.exec(
                        select(Product).where(Product.stock > 0, Product.name.contains(keywords[0])).limit(5)
                    ).all()
                    if not products:
                        logger.warning(f"No products for {niche_name}")
                        continue

                    # Generate ad content
                    video_paths = [self.content_generator.generate_ad_content(p.name) for p in products]
                    video_paths = [vp for vp in video_paths if vp]
                    if not video_paths:
                        logger.warning(f"No videos for {niche_name}")
                        continue

                    bundle_text = f"Ramadan {niche_name}! " + " | ".join([p.name for p in products[:3]]) + " (2-3 Days!)"
                    image_path = self.content_generator.generate_ad_image(products[0].name, bundle_text)

                    # Facebook Ad (docs: https://developers.facebook.com/docs/marketing-api/reference/ad_creative/)
                    account = AdAccount(f"act_{self.fb_account_id}")
                    creative_data = {
                        "name": f"{niche_name} Bundle",
                        "object_story_spec": {
                            "page_id": self.fb_page_id,
                            "video_data": {"video_file": open(video_paths[0], "rb").read()} if video_paths else {},
                            "image_url": image_path if image_path else None,
                            "call_to_action": {"type": "SHOP_NOW", "value": {"link": self.store_link}},
                            "message": bundle_text
                        }
                    }
                    creative = AdCreative(parent_id=f"act_{self.fb_account_id}").remote_create(params=creative_data)
                    ad = account.create_ad(params={
                        "name": f"{niche_name} Test",
                        "adset_id": self.fb_adset_id,
                        "creative": {"creative_id": creative["id"]},
                        "status": "ACTIVE",
                        "daily_budget": self.daily_budget
                    })

                    # TikTokio Ad (mock API, 2025)
                    tiktokio_key = os.getenv("TIKTOKIO_API_KEY")
                    tiktokio_headers = {"Authorization": f"Bearer {tiktokio_key}", "Content-Type": "application/json"}
                    tiktokio_payload = {
                        "video_url": video_paths[0] if video_paths else None,
                        "text": bundle_text,
                        "target": "UAE_Ramadan",
                        "budget": self.daily_budget / 100  # $5/day in dollars
                    }
                    resp_tiktok = requests.post("https://api.tiktokio.com/v1/ads", json=tiktokio_payload, headers=tiktokio_headers)
                    if resp_tiktok.status_code == 200:
                        logger.info(f"Created TikTokio ad for {niche_name}")

                    # Sieve Ad (mock API, 2025)
                    sieve_key = os.getenv("SIEVE_API_KEY")
                    sieve_headers = {"Authorization": f"Bearer {sieve_key}", "Content-Type": "application/json"}
                    sieve_payload = {
                        "video_url": video_paths[0] if video_paths else None,
                        "text": bundle_text,
                        "target": "UAE_Ramadan",
                        "budget": self.daily_budget / 100
                    }
                    resp_sieve = requests.post("https://api.sievedata.com/v1/ads", json=sieve_payload, headers=sieve_headers)
                    if resp_sieve.status_code == 200:
                        logger.info(f"Created Sieve ad for {niche_name}")

                    for vp in video_paths:
                        session.add(AdCampaign(video_id=vp.split('_')[1].split('.')[0], engagement_rate=0.0))
                    logger.info(f"Created {niche_name} ads: FB={ad['id']}")

                # Scale winners
                winners = session.exec(select(AdCampaign).where(AdCampaign.engagement_rate > 4.0)).all()
                if winners and self.daily_budget == 500:
                    self.daily_budget = 1500  # $15/day
                    for ad_id in session.exec(select(AdCampaign).where(AdCampaign.engagement_rate > 0)).all():
                        account.update_ad(ad_id, {"daily_budget": self.daily_budget // 3})
                    logger.info("Scaled budget to $15/day based on winners")
                session.commit()
            except Exception as e:
                logger.error(f"Campaign failed: {e}")
                session.rollback()