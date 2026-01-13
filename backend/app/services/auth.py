from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from loguru import logger

from app.core.database import get_db
from app.models import User
from app.services.user import UserService

security = HTTPBearer()

def verify_clerk_token(token: str) -> dict:
    """
    Mocked verification for base pipeline.
    """
    return {
        "email": "base@example.com",
        "first_name": "Base",
        "last_name": "User"
    }

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Returns a default user for the base pipeline.
    """
    user_service = UserService(db)
    user_data = {
        "email": "base@example.com",
        "first_name": "Base",
        "last_name": "User"
    }
    user = user_service.get_or_create_user(user_data)
    return user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    return get_current_user(credentials, db)