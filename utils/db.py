from sqlmodel import SQLModel, Field, create_engine
import os

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    cost: float
    price: float
    supplier_id: str
    stock: int = Field(default=0)

class Video(SQLModel, table=True):
    id: str = Field(primary_key=True)
    hashtag: str
    description: str

class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    video_id: str = Field(foreign_key="video.id")
    text: str
    analyzed: bool = Field(default=False)

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    status: str = Field(default="pending")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_agency")
engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)  # Creates tables on startup