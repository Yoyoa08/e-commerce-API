from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app import database, models, schemas, oauth2
from app.database import engine, get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# 1. Get all products (Public route with optional search/pagination)
@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(
    db: Session = Depends(database.get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = ""
):
    products = (
        db.query(models.Product)
        .filter(models.Product.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return products


# 2. Get a single product by ID (Public route)
@router.get("/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} was not found"
        )
    return product


# 3. Create a new product (Protected route - requires login)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_product = models.Product(owner_id=current_user.id, **product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


# 4. Delete a product (Protected route - owner only)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} does not exist"
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    product_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# 5. Update a product (Protected route - owner only)
@router.put("/{id}", response_model=schemas.ProductResponse)
def update_product(
    id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} does not exist"
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    product_query.update(updated_product.model_dump(), synchronize_session=False)
    db.commit()

    return product_query.first()