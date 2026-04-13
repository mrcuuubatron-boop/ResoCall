from fastapi import APIRouter, Request

from app.schemas import LoginRequest, LoginResponse
from app.security import build_token, verify_credentials

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request) -> LoginResponse:
    user = verify_credentials(payload.login, payload.password, request)
    return LoginResponse(
        ok=True,
        role=user.role,
        token=build_token(payload.login, payload.password),
    )
