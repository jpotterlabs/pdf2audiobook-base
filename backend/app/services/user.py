from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.models import User
from app.schemas import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_or_create_user(self, user_data: dict) -> User:
        """Get or create user by email."""
        user = self.get_user_by_email(user_data["email"])
        
        if user:
            # Update user info if needed
            if user_data.get("first_name") != user.first_name or \
               user_data.get("last_name") != user.last_name:
                user.first_name = user_data.get("first_name")
                user.last_name = user_data.get("last_name")
                self.db.commit()
                self.db.refresh(user)
            return user
        
        # Create new user
        user = User(
            email=user_data["email"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            auth_provider_id=user_data.get("auth_provider_id")
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user