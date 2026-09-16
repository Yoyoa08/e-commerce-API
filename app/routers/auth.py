from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, models, schemas, utils

router = APIRouter(prefix="/users", tags=["Users"])

