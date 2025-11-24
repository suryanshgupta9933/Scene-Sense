# core/security.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from core.auth import get_current_user

bearer = HTTPBearer()

def require_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer)
):
    token = credentials.credentials
    user_id = get_current_user(f"Bearer {token}")
    return user_id
