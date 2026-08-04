from fastapi import FastAPI

from database.db import Base, engine
from models import Investment

from routers.investment_router import router as investment_router
from routers.dashboard_router import router as dashboard_router
from routers.transaction_router import router as transaction_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EK Finance OS",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to EK Finance OS"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(
    investment_router,
    prefix="/investments",
    tags=["Investments"]
)

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    transaction_router
)