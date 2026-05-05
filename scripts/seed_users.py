from datetime import datetime
from uuid import uuid4

import app.models  # noqa: F401
from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User

#테스트용 계정 생성
SEED_USERS = [
    {
        "login_id": "engineer01",
        "password": "password123",
        "name": "Engineer One",
        "role": "USER",
    },
    {
        "login_id": "engineer02",
        "password": "password123",
        "name": "Engineer Two",
        "role": "USER",
    },
    {
        "login_id": "engineer03",
        "password": "password123",
        "name": "Engineer Three",
        "role": "USER",
    },
    {
        "login_id": "engineer04",
        "password": "password123",
        "name": "Engineer Four",
        "role": "USER",
    },
    {
        "login_id": "engineer05",
        "password": "password123",
        "name": "Engineer Five",
        "role": "USER",
    },
]


def seed_users() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for seed_user in SEED_USERS:
            existing_user = (
                db.query(User)
                .filter(User.login_id == seed_user["login_id"])
                .first()
            )

            if existing_user is not None:
                print(f"skip existing user: {seed_user['login_id']}")
                continue

            user = User(
                user_id=str(uuid4()),
                login_id=seed_user["login_id"],
                password_hash=hash_password(seed_user["password"]),
                name=seed_user["name"],
                role=seed_user["role"],
                created_at=datetime.now().isoformat(),
            )
            db.add(user)
            print(f"created user: {seed_user['login_id']}")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
