from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import uuid
import os

from db.session import get_db
from db.models import User

router = APIRouter()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


# -------------------------------
# Input schemas
# -------------------------------
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------------------
# Helper to create JWT
# -------------------------------
def create_jwt(user_id: str):
    expiry = datetime.now() + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {"sub": user_id, "exp": expiry}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# -------------------------------
# Helper to decode JWT + load user
# -------------------------------
def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(401, "Invalid auth scheme")
    except Exception:
        raise HTTPException(401, "Invalid Authorization header format")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user


# -------------------------------
# SIGNUP
# -------------------------------
@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "User already exists")
    
    count = db.query(User).count()
    if count >= 50:
        raise HTTPException(403, "User Limit reached")
    
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        password_hash=pwd.hash(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt(user.id)
    return {"token": token}


# -------------------------------
# LOGIN
# -------------------------------
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not pwd.verify(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_jwt(user.id)
    return {"token": token}

