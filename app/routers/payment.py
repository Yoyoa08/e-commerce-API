import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_user
from app.models import User

# Load Stripe secret key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-checkout-session")
def create_checkout_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Sample E-Commerce Product",
                        },
                        "unit_amount": 2000, # $20.00 in cents
                    },
                    "quantity": 1,
                },
            ],
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