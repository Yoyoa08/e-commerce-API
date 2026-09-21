from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_admin_user

router = APIRouter(prefix="/products", tags=["Products"])


# PUBLIC ROUTES
@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    products = (
        db.query(models.Product)
        .filter(models.Product.name.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return products


@router.get("/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} was not found",
        )

    return product


# ADMIN-ONLY ROUTES
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProductResponse,
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    # Pass owner_id using the authenticated admin's ID
    new_product = models.Product(
        owner_id=admin_user.id, **product.model_dump()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.put("/{id}", response_model=schemas.ProductResponse)
def update_product(
    id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} does not exist",
        )

    product_query.update(updated_product.model_dump(), synchronize_session=False)
    db.commit()

    return product_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} does not exist",
        )

    product_query.delete(synchronize_session=False)
    db.commit()

    return None