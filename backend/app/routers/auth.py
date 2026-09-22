from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import TokenResponse
from app.services.auth_service import (
    create_access_token,
    get_current_user
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "123456":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    token = create_access_token(form_data.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {
        "username": current_user,
        "message": "Acceso autorizado"
    }