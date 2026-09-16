from fastapi import FastAPI
from app.routers import auth, products

app = FastAPI(title="E-Commerce API")

app.include_router(products.router)


@app.get("/")
def root():
    return {"message": "Welcome to the E-Commerce API"}

#uvicorn app.main:app --reload