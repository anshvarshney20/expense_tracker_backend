import uuid
from typing import AsyncGenerator
from fastapi import Depends, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.repositories.user import UserRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError(message="Not authenticated")
    
    try:
        payload = security.decode_token(token, settings.SECRET_KEY)
        user_id = payload.get("sub")
        if user_id is None or payload.get("type") != "access":
            raise UnauthorizedError(message="Invalid token")
    except JWTError:
        raise UnauthorizedError(message="Could not validate credentials")
        
    user_repo = UserRepository(db)
    user = await user_repo.get(uuid.UUID(user_id))
    if not user:
        raise UnauthorizedError(message="User not found")
    if not user.is_active:
        raise UnauthorizedError(message="Inactive user")
    return user
