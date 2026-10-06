from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StrictBool, StrictFloat, StrictInt


class MerchantCategory(str, Enum):
    GROCERY = "grocery"
    ELECTRONICS = "electronics"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class TransactionSchema(BaseModel):
    user_id: Annotated[
        StrictInt,
        Field(gt=0)
    ]

    amount: Annotated[
        StrictFloat,
        Field(gt=0.0, le=100_000.0)
    ]

    merchant_category: MerchantCategory

    location_lat: Annotated[
        StrictFloat,
        Field(ge=-90.0, le=90.0)
    ]

    location_lon: Annotated[
        StrictFloat,
        Field(ge=-180.0, le=180.0)
    ]

    is_international: StrictBool = False


class PredictionResponseSchema(BaseModel):
    transaction_id: UUID
    timestamp: datetime
    is_fraud: bool
    fraud_probability: Annotated[
        float,
        Field(ge=0.0, le=1.0)
    ]
    risk_level: str