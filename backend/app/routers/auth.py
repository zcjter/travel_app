from datetime import datetime, timedelta
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse

from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["认证"])

SECRET_KEY = os.environ.get("CLOUDJOURNEY_SECRET", "cloudjourney-dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(status_code=401, detail="无效的认证凭证")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def optional_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(data.password) < 4:
        raise HTTPException(status_code=400, detail="密码长度不能少于4位")

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
    )
    db.add(user)
    await db.commit()

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录，返回 JWT token"""
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)
