from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    size = Column(String(10))
    color = Column(String(30))
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=5)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())