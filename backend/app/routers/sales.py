from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Sale, SaleItem, ProductVariant, Product
from ..schemas import SaleCreate, SaleResponse, SalesSummary

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Record a sale. Validates stock for every line FIRST (all-or-nothing),
    then snapshots price/cost and decrements stock. Never leaves a half-done
    transaction."""

    if not sale.items:
        raise HTTPException(status_code=400, detail="A sale needs at least one item.")

    # --- Phase 1: validate everything before touching stock ---
    resolved = []  # (variant, product, quantity)
    for line in sale.items:
        variant = (
            db.query(ProductVariant)
            .filter(ProductVariant.id == line.variant_id)
            .first()
        )
        if not variant:
            raise HTTPException(
                status_code=404, detail=f"Variant {line.variant_id} not found."
            )
        if not variant.is_active:
            raise HTTPException(
                status_code=400, detail=f"{variant.sku} is archived and cannot be sold."
            )
        if variant.stock_quantity < line.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {variant.sku}: "
                f"{variant.stock_quantity} left, {line.quantity} requested.",
            )
        product = db.query(Product).filter(Product.id == variant.product_id).first()
        resolved.append((variant, product, line.quantity))

    # --- Phase 2: build the sale, snapshot, decrement ---
    db_sale = Sale(
        payment_method=sale.payment_method or "cash",
        customer_name=sale.customer_name,
        note=sale.note,
    )

    total_amount = Decimal("0")
    total_cost = Decimal("0")

    for variant, product, qty in resolved:
        unit_price = variant.price
        unit_cost = variant.cost_price or Decimal("0")
        line_total = unit_price * qty

        db_sale.items.append(
            SaleItem(
                variant_id=variant.id,
                product_name=product.name if product else None,
                sku=variant.sku,
                size=variant.size,
                color=variant.color,
                quantity=qty,
                unit_price=unit_price,
                unit_cost=unit_cost,
                line_total=line_total,
            )
        )

        variant.stock_quantity -= qty  # decrement stock
        total_amount += line_total
        total_cost += unit_cost * qty

    db_sale.total_amount = total_amount
    db_sale.total_cost = total_cost

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=list[SaleResponse])
def list_sales(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Recent sales, newest first. `days` bounds how far back to look."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(Sale)
        .filter(Sale.created_at >= cutoff)
        .order_by(Sale.created_at.desc())
        .all()
    )


@router.get("/summary", response_model=SalesSummary)
def sales_summary(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Aggregated report for the last `days` days: revenue, cost, profit,
    a per-day breakdown, and the best-selling items."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    sales = (
        db.query(Sale)
        .filter(Sale.created_at >= cutoff)
        .order_by(Sale.created_at.asc())
        .all()
    )

    revenue = Decimal("0")
    cost = Decimal("0")
    items_sold = 0
    daily = {}   # date -> {sale_count, items_sold, revenue, profit}
    top = {}     # sku -> {product_name, quantity_sold, revenue}

    for s in sales:
        day = s.created_at.date()
        d = daily.setdefault(
            day,
            {"sale_count": 0, "items_sold": 0, "revenue": Decimal("0"), "profit": Decimal("0")},
        )
        d["sale_count"] += 1
        revenue += s.total_amount
        cost += s.total_cost
        d["revenue"] += s.total_amount
        d["profit"] += (s.total_amount - s.total_cost)

        for it in s.items:
            items_sold += it.quantity
            d["items_sold"] += it.quantity
            t = top.setdefault(
                it.sku,
                {"product_name": it.product_name, "quantity_sold": 0, "revenue": Decimal("0")},
            )
            t["quantity_sold"] += it.quantity
            t["revenue"] += it.line_total

    daily_list = [
        {
            "day": day,
            "sale_count": v["sale_count"],
            "items_sold": v["items_sold"],
            "revenue": v["revenue"],
            "profit": v["profit"],
        }
        for day, v in sorted(daily.items())
    ]

    top_list = sorted(
        (
            {
                "sku": sku,
                "product_name": v["product_name"],
                "quantity_sold": v["quantity_sold"],
                "revenue": v["revenue"],
            }
            for sku, v in top.items()
        ),
        key=lambda x: x["quantity_sold"],
        reverse=True,
    )[:5]

    return {
        "period_days": days,
        "sale_count": len(sales),
        "items_sold": items_sold,
        "revenue": revenue,
        "cost": cost,
        "profit": revenue - cost,
        "daily": daily_list,
        "top_products": top_list,
    }
