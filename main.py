from fastapi import FastAPI

app = FastAPI(title="Ecommerce API")

@app.get("/")
def root():
    return {"message": "Ecommerce API operational"}
