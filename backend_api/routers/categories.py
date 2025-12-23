from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend_api.db import models, database
from backend_api.routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["Categories"])

# -------------------------------------------------------
# ✅ Pydantic Schemas (v2)
# -------------------------------------------------------
class CategoryBase(BaseModel):
    name: str
    icon: str = "tag"
    budget: float = 0.0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    budget: float


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


# -------------------------------------------------------
# ✅ Get all categories for logged-in user
# -------------------------------------------------------
@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all categories owned by the logged-in user."""
    categories = (
        db.query(models.Category)
        .filter(models.Category.user_id == current_user.id)
        .all()
    )
    return categories  # ✅ return a plain list (frontend expects an array)


# -------------------------------------------------------
# ✅ Add new category
# -------------------------------------------------------
@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new category for the current user."""
    new_category = models.Category(
        name=category.name,
        icon=category.icon,
        budget=category.budget,
        user_id=current_user.id,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# -------------------------------------------------------
# ✅ Update category budget
# -------------------------------------------------------
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    updated: CategoryUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update the budget of an existing category."""
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id,
            models.Category.user_id == current_user.id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.budget = updated.budget
    db.commit()
    db.refresh(category)
    return category


# -------------------------------------------------------
# ✅ Delete a category
# -------------------------------------------------------
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a category by ID."""
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id,
            models.Category.user_id == current_user.id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": f"Category '{category.name}' deleted successfully"}
