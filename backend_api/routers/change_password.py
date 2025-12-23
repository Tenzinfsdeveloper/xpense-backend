from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
import os

from backend_api.db import database, models

# -------------------------------------------------------
# Router setup
# -------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------------
# Password helpers
# -------------------------------------------------------
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# -------------------------------------------------------
# Get current user from token
# -------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------------------------------------
# Change Password Schema
# -------------------------------------------------------
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# -------------------------------------------------------
# Change Password Endpoint
# -------------------------------------------------------
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):
    # Verify current password
    if not verify_password(payload.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Update password
    user.password = get_password_hash(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
