from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend_api.db import models, database
from backend_api.schemas import user_schema
from backend_api.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------------------------------------
# Get logged-in user's profile
# -------------------------------------------------------
@router.get("/me", response_model=user_schema.UserResponse)
def get_my_profile(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# -------------------------------------------------------
# Get all users
# -------------------------------------------------------
@router.get("/", response_model=list[user_schema.UserResponse])
def get_all_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()


# -------------------------------------------------------
# Get user by ID
# -------------------------------------------------------
@router.get("/{user_id}", response_model=user_schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------------------------------
# Update logged-in user (name + profile only)
# -------------------------------------------------------
class UserUpdate(BaseModel):
    name: str
    profile_image: str | None = None


@router.put("/me", response_model=user_schema.UserResponse)
def update_my_profile(
    updated: UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_user.name = updated.name
    current_user.profile_image = updated.profile_image

    db.commit()
    db.refresh(current_user)
    return current_user


# -------------------------------------------------------
# Delete user by ID
# -------------------------------------------------------
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}
