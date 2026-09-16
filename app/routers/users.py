from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app import database, models, schemas, oauth2, utils
from app.database import engine, get_db


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password using our new direct bcrypt function
    hashed_pwd = utils.hash_password(user.password)
    
    # Update the user object password with the hashed password
    new_user = models.User(email=user.email, password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
