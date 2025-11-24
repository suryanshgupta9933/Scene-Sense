# core/security.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException, Depends
from core.auth import get_current_user

from db.session import get_db
from db.models import User
from sqlalchemy.orm import Session

bearer = HTTPBearer()

def require_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer)
):
    token = credentials.credentials
    user_id = get_current_user(f"Bearer {token}")
    return user_id

def require_admin(user_id: str = Depends(require_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin privileges required")
    return user
