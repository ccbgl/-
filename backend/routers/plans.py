from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, TestTask, TestPlan
from schemas import PlanCreate, PlanResponse
from core.security import get_current_user

router = APIRouter(prefix="/tasks/{task_id}/plans", tags=["测试计划"])

@router.get("/", response_model=list[PlanResponse])
async def list_plans(task_id: int, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = (await db.execute(select(TestTask).where(TestTask.id == task_id))).scalar_one_or_none()
    if not task or (current.role != "admin" and task.creator_id != current.id):
        raise HTTPException(404, "任务不存在或无权限")
    res = await db.execute(select(TestPlan).where(TestPlan.task_id == task_id))
    return res.scalars().all()

@router.post("/", response_model=PlanResponse, status_code=201)
async def create_plan(task_id: int, data: PlanCreate, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = (await db.execute(select(TestTask).where(TestTask.id == task_id))).scalar_one_or_none()
    if not task or (current.role != "admin" and task.creator_id != current.id):
        raise HTTPException(404, "任务不存在或无权限")
    plan = TestPlan(task_id=task_id, name=data.name, plan_type=data.plan_type, cron_expr=data.cron_expr)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan