from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from backend_api.db import database, models

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "xpense_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------
# Helper functions
# -----------------------
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------
# Current user from token
# -----------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -----------------------
# Change Password Schema
# -----------------------
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# -----------------------
# Change Password
# -----------------------
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):

    # Step 1: Verify current password
    if not verify_password(payload.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Step 2: Update password
    user.password = get_password_hash(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
