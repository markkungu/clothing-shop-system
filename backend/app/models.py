from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Product(Base):
    """A style/design. The thing a customer thinks of as 'one product'
    (e.g. 'Adidas Sneaker'). It has no stock of its own — stock lives on
    its variants."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(60))
    category = Column(String(50))
    description = Column(Text)
    image_url = Column(String(255))  # reserved for later (item photos)
    is_active = Column(Boolean, default=True, nullable=False)  # soft-delete flag
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariant.id",
    )


class ProductVariant(Base):
    """A single sellable SKU: one size/color of a style, with its own
    price, cost and stock count. This is what a sale line will point to."""

    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    sku = Column(String(60), unique=True, index=True, nullable=False)
    size = Column(String(20))
    color = Column(String(30))
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=5)
    is_active = Column(Boolean, default=True, nullable=False)  # soft-delete flag
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="variants")


class Sale(Base):
    """One completed transaction at the till. Immutable audit record: it is
    never edited after creation, so the owner can reconcile it against cash."""

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    payment_method = Column(String(20), default="cash")
    customer_name = Column(String(100))
    note = Column(String(255))
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)  # revenue
    total_cost = Column(Numeric(12, 2), nullable=False, default=0)    # cost of goods

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        order_by="SaleItem.id",
    )


class SaleItem(Base):
    """A single line on a sale. Price/cost and product details are SNAPSHOTS
    copied at checkout, so reports and receipts stay correct even if the
    product is later renamed, repriced, or archived."""

    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)

    # --- snapshots at time of sale ---
    product_name = Column(String(100))
    sku = Column(String(60))
    size = Column(String(20))
    color = Column(String(30))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2))
    line_total = Column(Numeric(12, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    variant = relationship("ProductVariant")
