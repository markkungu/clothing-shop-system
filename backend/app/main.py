from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import products, variants, sales


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Clothing Shop Inventory API"
)


# Allow frontend access
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)



app.include_router(
    products.router
)

app.include_router(
    variants.router
)

app.include_router(
    sales.router
)



@app.get("/")
def read_root():

    return {
        "message": "Inventory API is running"
    }