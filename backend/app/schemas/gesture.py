from pydantic import BaseModel


class GestureResponse(BaseModel):
    action: str | None