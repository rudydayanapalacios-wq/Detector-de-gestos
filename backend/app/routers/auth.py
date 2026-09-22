from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.auth_service import (
    create_access_token,
    get_current_user
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    find_user
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


@router.post("/register")
def register(data: RegisterRequest):
    if not data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario es obligatorio"
        )

    if not data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es obligatoria"
        )

    if len(data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener mínimo 6 caracteres"
        )

    if find_user(data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está registrado"
        )

    create_user(data.username, data.password)

    return {
        "message": "Usuario registrado correctamente",
        "username": data.username
    }


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(user["username"])

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