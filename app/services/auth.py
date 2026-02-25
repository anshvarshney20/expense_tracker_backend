import uuid
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core import security
from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ValidationError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, user_in: UserCreate) -> User:
        user = await self.user_repo.get_by_email(user_in.email)
        if user:
            raise ValidationError(message="Email already registered")
        
        obj_in = {
            "email": user_in.email,
            "hashed_password": security.get_password_hash(user_in.password),
            "full_name": user_in.full_name,
            "currency": user_in.currency,
        }
        return await self.user_repo.create(obj_in=obj_in)

    async def authenticate(self, login_in: LoginRequest) -> User:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user:
            raise UnauthorizedError(message="Incorrect email or password")
        if not security.verify_password(login_in.password, user.hashed_password):
            raise UnauthorizedError(message="Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedError(message="Inactive user")
        return user

    def create_tokens(self, user_id: str) -> dict[str, str]:
        access_token = security.create_access_token(subject=user_id)
        refresh_token = security.create_refresh_token(subject=user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = security.decode_token(refresh_token, settings.REFRESH_SECRET_KEY)
            user_id = payload.get("sub")
            if not user_id or payload.get("type") != "refresh":
                raise UnauthorizedError(message="Invalid refresh token")
            
            return security.create_access_token(subject=user_id)
        except JWTError:
            raise UnauthorizedError(message="Could not validate credentials")

    async def generate_reset_token(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValidationError(message="No user found with this email")
        
        # Reset token expires in 15 minutes
        expires = timedelta(minutes=15)
        token = security.jwt.encode(
            {"exp": security.datetime.now(security.timezone.utc) + expires, "sub": str(user.id), "type": "reset"},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return token

    async def reset_password(self, token: str, new_password: str) -> None:
        try:
            payload = security.decode_token(token, settings.SECRET_KEY)
            user_id = payload.get("sub")
            if not user_id or payload.get("type") != "reset":
                raise ValidationError(message="Invalid or expired reset token")
            
            user = await self.user_repo.get(uuid.UUID(user_id))
            if not user:
                raise ValidationError(message="User not found")
            
            hashed_password = security.get_password_hash(new_password)
            await self.user_repo.update(db_obj=user, obj_in={"hashed_password": hashed_password})
        except JWTError:
            raise ValidationError(message="Invalid or expired reset token")

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not security.verify_password(current_password, user.hashed_password):
            raise ValidationError(message="Incorrect current password")
        
        hashed_password = security.get_password_hash(new_password)
        await self.user_repo.update(db_obj=user, obj_in={"hashed_password": hashed_password})
