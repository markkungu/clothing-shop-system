from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Product, ProductVariant
from ..schemas import VariantCreate, VariantUpdate, VariantResponse

router = APIRouter(tags=["Variants"])


@router.post(
    "/products/{product_id}/variants/",
    response_model=VariantResponse,
    status_code=201,
)
def add_variant(
    product_id: int, variant: VariantCreate, db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_variant = ProductVariant(product_id=product_id, **variant.model_dump())
    db.add(db_variant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="That SKU already exists.")
    db.refresh(db_variant)
    return db_variant


@router.put("/variants/{variant_id}", response_model=VariantResponse)
def update_variant(
    variant_id: int, changes: VariantUpdate, db: Session = Depends(get_db)
):
    variant = (
        db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    for key, value in changes.model_dump(exclude_unset=True).items():
        setattr(variant, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="That SKU already exists.")
    db.refresh(variant)
    return variant


@router.delete("/variants/{variant_id}", status_code=204)
def archive_variant(variant_id: int, db: Session = Depends(get_db)):
    """Soft-delete a single SKU so historical sales keep their reference."""
    variant = (
        db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant.is_active = False
    db.commit()
    return None
