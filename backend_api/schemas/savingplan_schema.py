from pydantic import BaseModel
from datetime import datetime

# Base fields for both request & response
class SavingPlanBase(BaseModel):
    goal: str
    target_amount: float
    duration: int
    saved_amount: float = 0

# Create request schema
class SavingPlanCreate(SavingPlanBase):
    pass

# Update saved amount schema
class SavingPlanUpdate(BaseModel):
    amount: float  # amount to ADD, not override

# Response schema
class SavingPlanResponse(SavingPlanBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True
