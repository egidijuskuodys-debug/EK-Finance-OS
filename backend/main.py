from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importuojame visus modelius, kad SQLAlchemy registruotu metadata
from models import (
    CashMovement,
    Dividend,
    ImportHistory,
    Investment,
    Transaction,
    TransactionLot,
)

from routers.analytics_router import router as analytics_router
from routers.dashboard_router import router as dashboard_router
from routers.dividend_router import router as dividend_router
from routers.import_history_router import (
    router as import_history_router,
)
from routers.import_router import router as import_router
from routers.investment_router import router as investment_router
from routers.market_data_router import router as market_data_router
from routers.transaction_router import router as transaction_router


app = FastAPI(
    title="EK Finance OS",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


app.include_router(investment_router)

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"],
)

app.include_router(transaction_router)

app.include_router(analytics_router)

app.include_router(market_data_router)

app.include_router(dividend_router)

app.include_router(import_router)

app.include_router(import_history_router)