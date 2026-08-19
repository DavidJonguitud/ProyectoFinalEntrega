from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate

from app.core.security import hash_password

class UserRepository:
    def __init__(self, db:Session):
        self.db =  db

    def create_user(self, user_data: UserCreate) -> User:

        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password = hashed_password
        )

        self.db.add(user)
        return user


    def get_user_by_email(self, email:str) -> User | None:
        user = self.db.query(User).filter(
            User.email == email
        ).first()
        return user 

