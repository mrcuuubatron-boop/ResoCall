from fastapi import Header, HTTPException, Request

from app.schemas import UserContext


def build_token(login: str, password: str) -> str:
    return f"demo-{login}-{password}"


def verify_credentials(login: str, password: str, request: Request) -> UserContext:
    ctx = request.app.state.ctx
    role = ctx.db.verify_user(login, password)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return UserContext(login=login, role=role)


def get_current_user(
    request: Request,
    x_login: str | None = Header(default=None),
    x_password: str | None = Header(default=None),
) -> UserContext:
    if not x_login or not x_password:
        raise HTTPException(status_code=401, detail="Missing auth headers: x-login and x-password")
    return verify_credentials(x_login, x_password, request)
