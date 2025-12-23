# backend_api/routers/expenses.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend_api.db import database, models
from backend_api.schemas import expense_schema
from backend_api.routers.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ------------------------------------
# GET ALL EXPENSES
# ------------------------------------
@router.get("/", response_model=list[expense_schema.ExpenseResponse])
def get_expenses(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    expenses = (
        db.query(models.Expense)
        .options(joinedload(models.Expense.category))  # category may be null
        .filter(models.Expense.user_id == current_user.id)
        .order_by(models.Expense.created_at.desc())
        .all()
    )
    return expenses


# ------------------------------------
# CREATE EXPENSE (category optional)
# ------------------------------------
@router.post("/", response_model=expense_schema.ExpenseResponse)
def create_expense(
    expense_data: expense_schema.ExpenseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):

    # 🔥 Category optional now
    if expense_data.category_id:
        category = (
            db.query(models.Category)
            .filter(
                models.Category.id == expense_data.category_id,
                models.Category.user_id == current_user.id,
            )
            .first()
        )
        if not category:
            # instead of blocking → simply ignore category, make it null
            expense_data.category_id = None

    new_expense = models.Expense(
        amount=expense_data.amount,
        description=expense_data.description,
        receipt_url=expense_data.receipt_url,
        user_id=current_user.id,
        category_id=expense_data.category_id,  # can be None
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    # reload with joined category (may be null)
    full_expense = (
        db.query(models.Expense)
        .options(joinedload(models.Expense.category))
        .filter(models.Expense.id == new_expense.id)
        .first()
    )

    return full_expense


# ------------------------------------
# DELETE EXPENSE
# ------------------------------------
@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = (
        db.query(models.Expense)
        .filter(
            models.Expense.id == expense_id,
            models.Expense.user_id == current_user.id,
        )
        .first()
    )

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": f"Expense {expense_id} deleted successfully"}
