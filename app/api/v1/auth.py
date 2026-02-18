from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.schemas.auth import Token
from app.api.schemas.users import UserCreate, UserPublic
from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token
from app.domain.users.service import authenticate_user, create_user

router = APIRouter()


@router.post("/register/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in.username, user_in.email, user_in.password)


@router.post("/login/", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout/")
def logout():
    return {"detail": "Logout is handled client-side (stateless tokens)."}