from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from backend_api.db import database, models

# -------------------------------------------------------
# ✅ Setup
# -------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "xpense_secret_key_123"  # ⚠️ Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------------
# ✅ Password Hashing Helpers
# -------------------------------------------------------
def get_password_hash(password: str):
    """Hashes a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Verifies that a plain password matches its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------------------------------
# ✅ JWT Token Creation
# -------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -------------------------------------------------------
# ✅ Decode token → Get current user
# -------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """Decodes JWT and returns the current user object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


# -------------------------------------------------------
# ✅ Login Endpoint (returns JWT)
# -------------------------------------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    """Authenticates a user and returns a JWT access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------------------------------------
# ✅ Signup Schema
# -------------------------------------------------------
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str


# -------------------------------------------------------
# ✅ Signup Endpoint (expects JSON)
# -------------------------------------------------------
@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(database.get_db)):
    """Registers a new user (and creates default 'No Category')."""
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = get_password_hash(payload.password)
    new_user = models.User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=hashed_pw,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # -------------------------------------------------------
    # ✅ Create default category for this user
    # -------------------------------------------------------
    default_category = models.Category(
        name="No Category",
        icon="tag",
        budget=0,
        user_id=new_user.id
    )

    db.add(default_category)
    db.commit()

    return {"message": "User created successfully", "user_id": new_user.id}

    """Registers a new user (expects JSON body)."""
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(payload.password)
    new_user = models.User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}
