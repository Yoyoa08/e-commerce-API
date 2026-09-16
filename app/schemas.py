from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# -----------------------------
# USER SCHEMAS
# -----------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# app/schemas.py

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime

# -----------------------------
# PRODUCT SCHEMAS
# -----------------------------
class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock: int = Field(ge=0, description="Stock cannot be negative")

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# -----------------------------
# ORDER & ORDER ITEM SCHEMAS
# -----------------------------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]


# -----------------------------
# AUTH / TOKEN SCHEMAS
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None