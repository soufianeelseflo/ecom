from sqlmodel import SQLModel, Field, create_engine
import os

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    cost: float
    price: float
    supplier_id: str
    stock: int = 0
    sales_count: int = 0
    revenue: float = 0.0

class Video(SQLModel, table=True):
    id: str = Field(primary_key=True)
    hashtag: str
    description: str
    used_in_ad: bool = False

class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    video_id: str = Field(foreign_key="video.id")
    text: str
    analyzed: bool = False
    sentiment: str = "NEUTRAL"

class AdCampaign(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    video_id: str = Field(foreign_key="video.id")
    engagement_rate: float = 0.0

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    status: str = "pending"
    supplier_order_id: str | None = None

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_agency")
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
SQLModel.metadata.create_all(engine)