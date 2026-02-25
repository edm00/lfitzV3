from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(100), unique=True)
    name = Column(String(500))
    brand = Column(String(200))
    price = Column(Float)
    currency = Column(String(10), default='USD')
    color = Column(String(100))
    description = Column(Text)
    image_url = Column(String(1000))
    product_url = Column(String(1000))
    category = Column(String(500))  # Google taxonomy
    sub_category = Column(String(200))  # Tops, Bottoms, etc.
    attributes = Column(Text)  # JSON string of additional attributes
    tags = Column(Text)  # JSON array of generated tags
    last_updated = Column(DateTime, default=datetime.utcnow)
    in_stock = Column(Boolean, default=True)
    
class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(100))
    price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///outfit_builder.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)