import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_factory
from models import Execution
from sqlalchemy import select
from redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("async_worker")

async def run_docker_test(exec_id: int, repo_url: str, exec_type: str):
    """真实执行流程：git clone -> docker build -> 执行用例 -> allure generate"""
    db: AsyncSession = async_session_factory()
    try:
        res = await db.execute(select(Execution).where(Execution.id == exec_id))
        rec = res.scalar_one_or_none()
        if not rec: return

        rec.status = "running"
        rec.start_time = datetime.utcnow()
        await db.commit()
        logger.info(f"▶️ 开始执行 [{exec_id}] | 仓库: {repo_url}")

        # 🐳 实际 Docker 执行逻辑（异步子进程）
        # proc = await asyncio.create_subprocess_exec(
        #     "docker", "run", "--rm", "-v", f"{repo_url}:/app", "python:3.9-slim",
        #     "/bin/bash", "-c", f"cd /app && pip install -r requirements.txt && pytest --alluredir=/tmp/allure-results"
        # )
        # await proc.communicate()

        # 🕒 模拟执行耗时
        await asyncio.sleep(3)

        # ✅ 模拟结果
        import random
        if random.random() > 0.2:
            rec.status = "success"
            rec.report_url = f"/reports/allure_{exec_id}/index.html"
            rec.logs = "✅ All tests passed. Allure report generated."
        else:
            rec.status = "failed"
            rec.logs = "❌ Assertion failed in test_api_login.py"

        rec.end_time = datetime.utcnow()
        await db.commit()
        logger.info(f"✅ 执行完成 [{exec_id}] | 状态: {rec.status}")

    except Exception as e:
        logger.error(f"💥 执行异常 [{exec_id}]: {str(e)}")
        if 'rec' in locals():
            rec.status = "failed"
            rec.logs = str(e)
            rec.end_time = datetime.utcnow()
            await db.commit()
    finally:
        await db.close()

async def start_worker():
    """后台异步消费者，持续从 Redis 队列拉取任务"""
    logger.info("🚀 异步任务消费者已启动")
    while True:
        try:
            data = await redis_client.brpop("autotest:queue", timeout=2)
            if data:
                _, payload = data
                task = json.loads(payload)
                asyncio.create_task(run_docker_test(task["exec_id"], task["repo_url"], task["exec_type"]))
        except Exception as e:
            logger.error(f"Worker 异常: {e}")
            await asyncio.sleep(1)