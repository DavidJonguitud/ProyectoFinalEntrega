from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session 
from app.models.user import User
from app.repositories.user import UserRepository

from app.core.security import verify_password, create_access_token, create_refresh_token

import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.repo = user_repo


    async def create_user(self, user_data: UserCreate) -> dict:
        if await self.user_exists(user_data.email):
            logger.warning("User already exists")
            raise ValueError("User already exists")
   
        user = self.repo.create_user(user_data)
      
        try:
            self.db.commit()
            self.db.refresh(user)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Could not commit {e}")
            raise Exception(f"Could not commit: {e}")
        
        return user

    async def user_exists(self, email: str) -> bool:
        return self.repo.get_user_by_email(email) is not None

    async def login_user(self, user_data: UserLogin) -> User:
        user = self.repo.get_user_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            logger.warning("Invalid Credentials")
            raise ValueError("Invalid Credentials")

        return {
            "access_token": create_access_token(user_data.email),
            "refresh_token": create_refresh_token(user_data.email),
            "token_type": "bearer",
            "user": user
        }

    def get_user_by_email(self, user_email: str):
        return self.repo.get_user_by_email(user_email)