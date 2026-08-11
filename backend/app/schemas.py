from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime, date


# --------------------------------------------------------------------------- #
# Variant (a single sellable SKU: one size/color of a style)
# --------------------------------------------------------------------------- #
class VariantBase(BaseModel):
    sku: str
    size: Optional[str] = None
    color: Optional[str] = None
    price: Decimal
    cost_price: Optional[Decimal] = None
    stock_quantity: int = 0
    reorder_level: int = 5
    is_active: bool = True


class VariantCreate(VariantBase):
    pass


class VariantUpdate(BaseModel):
    """Every field optional — send only what changes (e.g. just stock)."""

    sku: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    is_active: Optional[bool] = None


class VariantResponse(VariantBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
# Product (a style; owns many variants)
# --------------------------------------------------------------------------- #
class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    # A style may be created together with its first variants in one call.
    variants: list[VariantCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    variants: list[VariantResponse] = []

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
# Sales
# --------------------------------------------------------------------------- #
class SaleItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    payment_method: Optional[str] = "cash"
    customer_name: Optional[str] = None
    note: Optional[str] = None
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleItemResponse(BaseModel):
    id: int
    variant_id: int
    product_name: Optional[str] = None
    sku: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    quantity: int
    unit_price: Decimal
    unit_cost: Optional[Decimal] = None
    line_total: Decimal

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    created_at: datetime
    payment_method: Optional[str] = None
    customer_name: Optional[str] = None
    note: Optional[str] = None
    total_amount: Decimal
    total_cost: Decimal
    items: list[SaleItemResponse] = []

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #
class DailySales(BaseModel):
    day: date
    sale_count: int
    items_sold: int
    revenue: Decimal
    profit: Decimal


class TopProduct(BaseModel):
    sku: str
    product_name: Optional[str] = None
    quantity_sold: int
    revenue: Decimal


class SalesSummary(BaseModel):
    period_days: int
    sale_count: int
    items_sold: int
    revenue: Decimal
    cost: Decimal
    profit: Decimal
    daily: list[DailySales] = []
    top_products: list[TopProduct] = []
