from fastapi import Header, HTTPException

from app.schemas import UserContext

# Minimal demo auth, matching current frontend credentials.
USERS: dict[str, dict[str, str]] = {
    "admin": {"password": "admin", "role": "admin"},
    "engineer": {"password": "engineer", "role": "engineer"},
    "user": {"password": "user", "role": "user"},
}


def build_token(login: str, password: str) -> str:
    return f"demo-{login}-{password}"


def verify_credentials(login: str, password: str) -> UserContext:
    account = USERS.get(login)
    if account is None or account["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return UserContext(login=login, role=account["role"])


def get_current_user(
    x_login: str | None = Header(default=None),
    x_password: str | None = Header(default=None),
) -> UserContext:
    if not x_login or not x_password:
        raise HTTPException(status_code=401, detail="Missing auth headers: x-login and x-password")
    return verify_credentials(x_login, x_password)
