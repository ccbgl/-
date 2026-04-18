from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, TestPlan, Execution
from schemas import ExecutionResponse, PlanType
from core.security import get_current_user
from datetime import datetime
from redis_client import redis_client
import json

router = APIRouter(prefix="/plans/{plan_id}", tags=["执行管理"])

@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_run(plan_id: int, exec_type: PlanType = PlanType.full, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan = (await db.execute(select(TestPlan).where(TestPlan.id == plan_id))).scalar_one_or_none()
    if not plan or (current.role != "admin" and plan.task.creator_id != current.id):
        raise HTTPException(404, "计划不存在或无权限")

    exec_rec = Execution(plan_id=plan_id, status="pending", start_time=datetime.utcnow())
    db.add(exec_rec)
    await db.commit()
    await db.refresh(exec_rec)

    # 推入异步队列
    await redis_client.lpush("autotest:queue", json.dumps({
        "exec_id": exec_rec.id, "repo_url": plan.task.repo_url, "exec_type": exec_type.value
    }))

    exec_rec.status = "running"
    await db.commit()
    return {"job_id": exec_rec.id, "status": "queued"}

@router.get("/executions", response_model=list[ExecutionResponse])
async def list_executions(plan_id: int, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan = (await db.execute(select(TestPlan).where(TestPlan.id == plan_id))).scalar_one_or_none()
    if not plan or (current.role != "admin" and plan.task.creator_id != current.id):
        raise HTTPException(404, "无权限")
    res = await db.execute(select(Execution).where(Execution.plan_id == plan_id).order_by(Execution.created_at.desc()))
    return res.scalars().all()

@router.get("/executions/{exec_id}/report", response_model=ExecutionResponse)
async def get_report(exec_id: int, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rec = (await db.execute(select(Execution).where(Execution.id == exec_id))).scalar_one_or_none()
    if not rec or (current.role != "admin" and rec.plan.task.creator_id != current.id):
        raise HTTPException(404, "记录不存在")
    return rec