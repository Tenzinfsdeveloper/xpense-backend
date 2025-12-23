# backend_api/schemas/expense_schema.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from backend_api.schemas.category_schema import CategoryResponse


class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    category_id: Optional[int] = None   # 🔥 allow null


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime

    # 🔥 category can be null now
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
