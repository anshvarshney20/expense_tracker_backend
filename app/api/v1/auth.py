from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.core.security_limiter import limiter
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.schemas.responses import SuccessResponse
from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.services.auth import AuthService
from app.models.user import User
from app.repositories.user import UserRepository

router = APIRouter()


@router.post("/register", response_model=SuccessResponse[UserInDB])
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.register(user_in)
    return SuccessResponse(
        data=UserInDB.model_validate(user),
        message="User registered successfully"
    )


@router.post("/login", response_model=SuccessResponse[UserInDB])
@limiter.limit("5/minute")
async def login(
    login_in: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(deps.get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.authenticate(login_in)
    tokens = auth_service.create_tokens(str(user.id))
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    
    return SuccessResponse(
        data=UserInDB.model_validate(user),
        message="Login successful"
    )


@router.post("/refresh", response_model=SuccessResponse[None])
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from app.core.exceptions import UnauthorizedError
        raise UnauthorizedError(message="Refresh token missing")
        
    auth_service = AuthService(db)
    new_access_token = await auth_service.refresh_access_token(refresh_token)
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    
    return SuccessResponse(message="Token refreshed successfully")


@router.post("/logout", response_model=SuccessResponse[None])
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return SuccessResponse(message="Logged out successfully")


@router.get("/me", response_model=SuccessResponse[UserInDB])
async def get_me(current_user: User = Depends(deps.get_current_user)):
    return SuccessResponse(data=UserInDB.model_validate(current_user))


@router.post("/forgot-password", response_model=SuccessResponse[str])
async def forgot_password(
    request_in: ForgotPasswordRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    auth_service = AuthService(db)
    token = await auth_service.generate_reset_token(request_in.email)
    # In a real app, send this via email. For now, we return it.
    return SuccessResponse(data=token, message="Reset token generated")


@router.post("/reset-password", response_model=SuccessResponse[None])
async def reset_password(
    request_in: ResetPasswordRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    auth_service = AuthService(db)
    await auth_service.reset_password(request_in.token, request_in.new_password)
    await db.commit()
    return SuccessResponse(message="Password reset successfully")


@router.post("/change-password", response_model=SuccessResponse[None])
async def change_password(
    request_in: ChangePasswordRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    auth_service = AuthService(db)
    await auth_service.change_password(current_user, request_in.current_password, request_in.new_password)
    await db.commit()
    return SuccessResponse(message="Password changed successfully")


@router.patch("/me", response_model=SuccessResponse[UserInDB])
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    user_repo = UserRepository(db)
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        from app.core import security
        update_data["hashed_password"] = security.get_password_hash(update_data.pop("password"))
        
    updated_user = await user_repo.update(db_obj=current_user, obj_in=update_data)
    await db.commit()
    await db.refresh(updated_user)
    return SuccessResponse(
        data=UserInDB.model_validate(updated_user),
        message="Profile updated successfully"
    )
