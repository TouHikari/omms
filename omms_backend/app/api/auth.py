from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_session
from app.models.user import User
from app.core.auth import get_current_user
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LoginData,
    RegisterRequest,
    RegisterResponse,
    UserOut,
)
from app.settings import settings


router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    summary="用户注册",
    description="创建基础用户账户，默认赋予 PATIENT 身份。",
    response_model=RegisterResponse,
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(User).where(User.username == payload.username))
    if exists.scalars().first():
        return err(400, "用户名已存在")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = User(
        username=payload.username,
        password=get_password_hash(payload.password),
        email=payload.email,
        phone=payload.phone,
        real_name=payload.realName,
        status=1,
        created_at=now,
        updated_at=now,
        role_id=3,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return ok(
        UserOut(
            userId=user.user_id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            realName=user.real_name,
            roleId=user.role_id,
        )
    )


@router.post(
    "/auth/login",
    summary="用户登录",
    description="支持使用用户名或邮箱登录，返回 JWT 令牌。",
    response_model=LoginResponse,
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    res = await session.execute(
        select(User).where((User.username == payload.username) | (User.email == payload.username))
    )
    user = res.scalars().first()
    if not user:
        return err(401, "用户名或密码错误")
    if user.status != 1:
        return err(403, "用户已禁用")
    if not verify_password(payload.password, user.password):
        return err(401, "用户名或密码错误")
    user.last_login_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await session.commit()
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    token = create_access_token(
        subject=str(user.user_id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra={"username": user.username, "roleId": user.role_id},
    )
    return ok(
        LoginData(
            accessToken=token,
            tokenType="bearer",
            expiresIn=expires_in,
            user=UserOut(
                userId=user.user_id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                realName=user.real_name,
                roleId=user.role_id,
            ),
        )
    )


@router.get(
    "/auth/me",
    summary="当前用户信息",
    description="返回当前登录用户的基础信息。",
    response_model=RegisterResponse,
)
async def me(current: User = Depends(get_current_user)):
    return ok(
        UserOut(
            userId=current.user_id,
            username=current.username,
            email=current.email,
            phone=current.phone,
            realName=current.real_name,
            roleId=current.role_id,
        )
    )
