from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = ""
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
            detail=f"Product with id: {id} was not found"
        )
    return product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_product = models.Product(owner_id=current_user.id, **product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put("/{id}", response_model=schemas.ProductResponse)
def update_product(
    id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} does not exist"
        )

    product_query.update(updated_product.model_dump(), synchronize_session=False)
    db.commit()
    return product_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} does not exist"
        )

    product_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)