from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.OrderResponse)
def checkout(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # 1. Fetch user's cart
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your cart is empty")

    total_price = 0.0
    order_items = []

    # 2. Validate stock, lock price, and calculate total
    for item in cart.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {item.product_id} no longer exists")
        
        if product.stock < item.quantity:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product: '{product.name}' (Available: {product.stock})"
            )

        item_total = product.price * item.quantity
        total_price += item_total

        # Prepare OrderItem record
        order_items.append(
            models.OrderItem(product_id=product.id, quantity=item.quantity, price_at_purchase=product.price))

        # Deduct stock
        product.stock -= item.quantity

    # 3. Create Order
    new_order = models.Order(
        user_id=current_user.id,
        total_price=total_price,
        status="pending",
        items=order_items
    )

    db.add(new_order)

    # 4. Clear cart items
    for item in cart.items:
        db.delete(item)

    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/", response_model=list[schemas.OrderResponse])
def get_user_orders(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders


@router.get("/{id}", response_model=schemas.OrderResponse)
def get_order_by_id(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    order = db.query(models.Order).filter(
        models.Order.id == id,
        models.Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {id} not found")

    return order