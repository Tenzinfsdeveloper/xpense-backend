from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_api.db.database import get_db
from backend_api.db.models import SavingPlan, User
from backend_api.schemas.savingplan_schema import (
    SavingPlanCreate,
    SavingPlanResponse,
    SavingPlanUpdate
)
from backend_api.routers.auth import get_current_user

router = APIRouter(
    prefix="/saving-plans",
    tags=["Saving Plans"]
)


# ✔ Get all saving plans of logged-in user
@router.get("/", response_model=list[SavingPlanResponse])
def get_saving_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plans = db.query(SavingPlan).filter(SavingPlan.user_id == current_user.id).all()
    return plans


# ✔ Create a new saving plan
@router.post("/", response_model=SavingPlanResponse)
def create_saving_plan(
    plan: SavingPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_plan = SavingPlan(
        goal=plan.goal,
        target_amount=plan.target_amount,
        duration=plan.duration,
        saved_amount=plan.saved_amount,
        user_id=current_user.id
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


# ✔ Add saved amount (Increment)
@router.put("/{plan_id}", response_model=SavingPlanResponse)
def update_saving_amount(
    plan_id: int,
    update: SavingPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SavingPlan).filter(
        SavingPlan.id == plan_id,
        SavingPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Saving plan not found.")

    if update.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")

    plan.saved_amount += update.amount
    db.commit()
    db.refresh(plan)

    return plan


# ✔ Delete a saving plan
@router.delete("/{plan_id}")
def delete_saving_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SavingPlan).filter(
        SavingPlan.id == plan_id,
        SavingPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Saving plan not found.")

    db.delete(plan)
    db.commit()

    return {"message": "Saving plan deleted."}
