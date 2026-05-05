from sqlalchemy.orm import Session
from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_login_id(self, login_id: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.login_id == login_id)
            .first()
        )
    
    def find_by_user_id(self, user_id: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )