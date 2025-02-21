from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
from utils.db import engine, Product
from utils.logger import logger
from sqlmodel import Session, select

class AdManager:
    def __init__(self, fb_access_token, tt_access_token, content_generator):
        FacebookAdsApi.init(access_token=fb_access_token)
        self.fb_account_id = "your_fb_ad_account_id"  # Replace with your account ID
        self.fb_adset_id = "your_fb_adset_id"  # Replace with your ad set ID
        # self.tt_client = TikTokClient(tt_access_token)  # Placeholder
        self.content_generator = content_generator

    def run_campaigns(self):
        with Session(engine) as session:
            try:
                products = session.exec(select(Product)).all()
                for product in products:
                    ad_content = self.content_generator.generate_ad_content(product.name)
                    if ad_content:
                        # Facebook Ad
                        creative_data = {
                            "name": f"{product.name} Ad",
                            "object_story_spec": {
                                "page_id": "your_page_id",  # Replace with your page ID
                                "link_data": {
                                    "message": ad_content,
                                    "link": "https://yourstore.com",
                                    "call_to_action": {"type": "SHOP_NOW"}
                                }
                            }
                        }
                        self.create_fb_ad(creative_data)
                        # TikTok Ad (Placeholder)
                        self.create_tt_ad(product.name, ad_content)
            except Exception as e:
                logger.error(f"Ad campaign failed: {e}")

    def create_fb_ad(self, creative_data):
        account = AdAccount(f"act_{self.fb_account_id}")
        creative = AdCreative(parent_id=f"act_{self.fb_account_id}").remote_create(params=creative_data)
        ad = account.create_ad(params={
            "name": "AI Agency Ad",
            "adset_id": self.fb_adset_id,
            "creative": {"creative_id": creative["id"]},
            "status": "PAUSED"  # Set to "ACTIVE" when ready
        })
        logger.info(f"Created Facebook ad: {ad['id']}")

    def create_tt_ad(self, product_name, ad_content):
        # Placeholder for TikTok Marketing API
        logger.info(f"Simulated TikTok ad for {product_name}: {ad_content}")