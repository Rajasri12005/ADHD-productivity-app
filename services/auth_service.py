from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from models.streak import Streak
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def signup(email: str, password: str, username: str | None, db: Session) -> dict:
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=email,
        password_hash=hash_password(password),
        username=username,
    )
    db.add(user)
    db.flush()  # get user.id

    # Bootstrap streak row
    streak = Streak(user_id=user.id, current_streak=0, longest_streak=0)
    db.add(streak)
    db.commit()
    db.refresh(user)

    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def login(email: str, password: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )

    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def refresh_tokens(refresh_token: str, db: Session) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}
