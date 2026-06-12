from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from schemas import SignupRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from services import signup, login, refresh_tokens
from models.user import User

router = APIRouter(tags=["auth"])


@router.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user. Returns access + refresh tokens.
    Duplicate email returns 409.
    """
    return signup(payload.email, payload.password, payload.username, db)


@router.post("/auth/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive access + refresh tokens."""
    return login(payload.email, payload.password, db)


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_route(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new token pair."""
    return refresh_tokens(payload.refresh_token, db)


@router.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    """
    Stateless logout — client must delete the token.
    Returns 204. No server-side token invalidation (use short-lived tokens).
    """
    return None
