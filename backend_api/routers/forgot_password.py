from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
import os

from backend_api.db.database import get_db
from backend_api.db import models
from backend_api.routers.auth import get_password_hash

# -------------------------------------------------------
# Router Setup
# -------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Password Reset"])

RESET_SECRET_KEY = os.getenv("RESET_SECRET_KEY")
ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 30

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Safety checks (fail fast)
if not RESET_SECRET_KEY:
    raise ValueError("RESET_SECRET_KEY is not set")
if not SMTP_EMAIL or not SMTP_PASSWORD:
    raise ValueError("SMTP_EMAIL or SMTP_PASSWORD is not set")

# -------------------------------------------------------
# Schemas
# -------------------------------------------------------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# -------------------------------------------------------
# Create reset token
# -------------------------------------------------------
def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, RESET_SECRET_KEY, algorithm=ALGORITHM)


# -------------------------------------------------------
# Verify reset token
# -------------------------------------------------------
def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired reset token")


# -------------------------------------------------------
# Send reset email
# -------------------------------------------------------
def send_reset_email(to_email: str, reset_link: str):
    message = EmailMessage()
    message["Subject"] = "Reset Your XPense Password"
    message["From"] = SMTP_EMAIL
    message["To"] = to_email

    message.set_content(
        f"""
Hello,

Click the link below to set a NEW password for your XPense account:

{reset_link}

This link expires in 30 minutes.

If you did not request this, you may safely ignore this email.
"""
    )

    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
    smtp.send_message(message)
    smtp.quit()


# -------------------------------------------------------
# Forgot Password (Send Link)
# -------------------------------------------------------
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    token = create_reset_token(request.email)

    reset_link = (
        f"https://regal-sorbet-c2cac0.netlify.app/reset_password.html?token={token}"
    )

    send_reset_email(request.email, reset_link)

    return {"message": "Password reset link sent to your email"}


# -------------------------------------------------------
# Reset Password
# -------------------------------------------------------
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):

    email = verify_reset_token(request.token)

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = get_password_hash(request.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
