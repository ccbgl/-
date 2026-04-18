from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, TestTask
from schemas import TaskCreate, TaskResponse
from core.security import get_current_user
from config import settings

router = APIRouter(prefix="/tasks", tags=["测试任务"])

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(skip: int = 0, limit: int = 20, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(TestTask).order_by(TestTask.created_at.desc())
    if current.role != "admin": stmt = stmt.where(TestTask.creator_id == current.id)
    res = await db.execute(stmt.offset(skip).limit(limit))
    return res.scalars().all()

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = TestTask(name=data.name, description=data.description or "", repo_url=data.repo_url or settings.REPO_URL, creator_id=current.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task