from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import products, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API")

app.include_router(users.router)
app.include_router(products.router)


@app.get("/")
def root():
    return {"message": "Welcome to the E-Commerce API"}