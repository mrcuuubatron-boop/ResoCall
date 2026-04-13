from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas import ErrorOut, ModuleSettingsIn, ModuleSettingsOut, UserContext
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/modules", tags=["modules"])


@router.get(
    "/{module_key}/settings",
    response_model=ModuleSettingsOut,
    responses={400: {"model": ErrorOut}},
)
def get_module_settings(
    module_key: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> ModuleSettingsOut:
    module_key = module_key.strip()
    if not module_key:
        raise HTTPException(status_code=400, detail="module_key is required")

    settings, updated_at = request.app.state.ctx.storage.read_module_settings(user.login, module_key)
    return ModuleSettingsOut(module_key=module_key, settings=settings, updated_at=updated_at)


@router.put(
    "/{module_key}/settings",
    response_model=ModuleSettingsOut,
    responses={400: {"model": ErrorOut}},
)
def save_module_settings(
    module_key: str,
    payload: ModuleSettingsIn,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> ModuleSettingsOut:
    module_key = module_key.strip()
    if not module_key:
        raise HTTPException(status_code=400, detail="module_key is required")

    updated_at = request.app.state.ctx.storage.write_module_settings(user.login, module_key, payload.settings)
    return ModuleSettingsOut(module_key=module_key, settings=payload.settings, updated_at=updated_at)
