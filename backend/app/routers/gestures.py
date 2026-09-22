import cv2
import numpy as np

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.schemas.gesture import GestureResponse
from app.services.auth_service import get_current_user
from app.services.gesture_service import GestureService


router = APIRouter(
    prefix="/api/v1",
    tags=["Gestos"]
)

gesture_service = GestureService()


@router.post(
    "/recognize-action",
    response_model=GestureResponse,
    summary="Reconocer gesto",
    description=(
        "Recibe una imagen de una mano y utiliza MediaPipe "
        "para identificar el gesto realizado."
    ),
    responses={
        400: {
            "description": "El archivo no es una imagen válida "
            "o no pudo ser procesado."
        },
        401: {
            "description": "No se proporcionó un token válido."
        }
    }
)
async def recognize_action(
    file: UploadFile = File(
        ...,
        description="Imagen que contiene la mano del usuario."
    ),
    current_user: str = Depends(get_current_user)
):
    """
    Analiza una imagen y reconoce una acción gestual.
    """

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen"
        )

    contents = await file.read()

    image_array = np.frombuffer(
        contents,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="No se pudo procesar la imagen"
        )

    action = gesture_service.process_image(image)

    return {
        "action": action
    }


@router.get(
    "/menu-shortcuts",
    summary="Consultar acciones disponibles",
    description=(
        "Devuelve el mapa de gestos disponibles y la acción "
        "asociada a cada uno."
    ),
    responses={
        401: {
            "description": "No se proporcionó un token válido."
        }
    }
)
def menu_shortcuts(
    current_user: str = Depends(get_current_user)
):
    """
    Consulta los gestos y acciones soportados por el sistema.
    """

    return {
        "gestures": {
            "Pointing_Up": "SELECT",
            "Open_Palm": "BACK",
            "Thumb_Up": "SWIPE_RIGHT"
        }
    } 