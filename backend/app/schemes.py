from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    price: Decimal
    cost_price: Optional[Decimal] = None
    stock_quantity: int = 0
    reorder_level: int = 5


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True