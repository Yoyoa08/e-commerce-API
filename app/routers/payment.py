import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_user
from app.models import User, Cart

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-checkout-session")
def create_checkout_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Stripe secret key is not configured in environment variables."
        )

    # 1. Get the user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    # 2. Check if cart exists and has items
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Your cart is empty."
        )

    try:
        # 3. Build line items dynamically from CartItem -> Product relationship
        line_items = []
        for cart_item in cart.items:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": cart_item.product.name,
                    },
                    "unit_amount": int(cart_item.product.price * 100),  # Convert dollars to cents
                },
                "quantity": cart_item.quantity,
            })

        # 4. Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:8000/payments/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/payments/cancel",
        )
        
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/success")
def payment_success(session_id: str):
    return {"message": "Payment successful!", "session_id": session_id}

@router.get("/cancel")
def payment_cancel():
    return {"message": "Payment was cancelled."}