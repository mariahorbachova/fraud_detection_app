from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from typing import List

from src.schemas import (
    PredictionResponseSchema,
    TransactionSchema,
)


MODEL_PATH = Path("models/model.joblib")
LOG_PATH = Path("logs/suspicious_transactions.log")


def log_suspicious_transaction(
    transaction_id: UUID,
    probability: float,
    risk_level: str,
) -> None:
    """
    Записує інформацію про HIGH-risk транзакцію у лог-файл.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    log_line = (
        f"{timestamp} | "
        f"transaction_id={transaction_id} | "
        f"fraud_probability={probability:.4f} | "
        f"risk_level={risk_level}\n"
    )

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(log_line)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Завантаження ML-моделі один раз під час запуску застосунку.
    """
    app.state.model = None

    if MODEL_PATH.exists():
        app.state.model = joblib.load(MODEL_PATH)

    yield

    app.state.model = None


app = FastAPI(
    title="Fraud Detection API",
    description="REST API для прогнозування шахрайських транзакцій",
    version="1.0.0",
    lifespan=lifespan,
)


def calculate_risk_level(probability: float) -> str:
    """
    Визначає рівень ризику за ймовірністю шахрайства.
    """
    if probability < 0.3:
        return "LOW"

    if probability < 0.7:
        return "MEDIUM"

    return "HIGH"


def predict_transaction(
    transaction: TransactionSchema,
    model,
) -> tuple[float, bool, str]:
    """
    Виконує prediction для однієї транзакції.
    """

    data = pd.DataFrame(
        [
            {
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "merchant_category": transaction.merchant_category.value,
                "location_lat": transaction.location_lat,
                "location_lon": transaction.location_lon,
                "is_international": transaction.is_international,
            }
        ]
    )

    probability = float(model.predict_proba(data)[0][1])

    probability = round(probability, 4)

    is_fraud = probability >= 0.5

    risk_level = calculate_risk_level(probability)

    return probability, is_fraud, risk_level


@app.get("/health")
def health_check():
    """
    Перевірка стану API та завантаження моделі.
    """

    model = getattr(app.state, "model", None)

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    return {
        "status": "ok",
        "model_loaded": True,
    }


@app.post(
    "/v1/predict",
    response_model=PredictionResponseSchema,
)
def predict(
    transaction: TransactionSchema,
    background_tasks: BackgroundTasks,
):
    """
    Прогноз шахрайства для однієї транзакції.
    """

    model = getattr(app.state, "model", None)

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    probability, is_fraud, risk_level = predict_transaction(
        transaction,
        model,
    )

    transaction_id = uuid4()

    timestamp = datetime.now(timezone.utc)

    if risk_level == "HIGH":
        background_tasks.add_task(
            log_suspicious_transaction,
            transaction_id,
            probability,
            risk_level,
        )

    return PredictionResponseSchema(
        transaction_id=transaction_id,
        timestamp=timestamp,
        is_fraud=is_fraud,
        fraud_probability=probability,
        risk_level=risk_level,
    )


@app.post(
    "/v1/predict/batch",
    response_model=List[PredictionResponseSchema],
)
def predict_batch(
    transactions: List[TransactionSchema],
):
    """
    Прогноз шахрайства для пакета транзакцій.

    Максимальний розмір пакета — 50 транзакцій.
    """

    if len(transactions) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum batch size is 50 transactions",
        )

    model = getattr(app.state, "model", None)

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    results = []

    for transaction in transactions:
        probability, is_fraud, risk_level = predict_transaction(
            transaction,
            model,
        )

        results.append(
            PredictionResponseSchema(
                transaction_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                is_fraud=is_fraud,
                fraud_probability=probability,
                risk_level=risk_level,
            )
        )

    return results