from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserResponse
from core.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(form: UserLogin, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == form.username))
    user = res.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建用户")
    if await db.execute(select(User).where(User.username == data.username)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password_hash=get_password_hash(data.password), role=data.role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
async def get_me(current: User = Depends(get_current_user)):
    return current