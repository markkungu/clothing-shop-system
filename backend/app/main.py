from fastapi import FastAPI
from .database import Base, engine
from .routers import products

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clothing Shop Inventory API")

app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Inventory API is running"}