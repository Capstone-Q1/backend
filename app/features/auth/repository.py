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
    
    def update_refresh_token_hash(
        self,
        user_id: str,
        refresh_token_hash: str,
    ) -> None:
        user = self.find_by_user_id(user_id)

        if user is None:
            return

        user.refresh_token_hash = refresh_token_hash
        self.db.commit()
        
    def clear_refresh_token_hash(self, user_id: str) -> None:
        user = self.find_by_user_id(user_id)

        if user is None:
            return

        user.refresh_token_hash = None #NULL이라고 보면 됨
        self.db.commit()