from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from routers import auth, tasks, plans, executions
from core.worker import start_worker
from database import engine, Base
from redis_client import redis_client
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动建表 & 启动异步消费者
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    worker_task = asyncio.create_task(start_worker())
    yield
    # 关闭时：清理资源
    worker_task.cancel()
    await redis_client.aclose()

app = FastAPI(title="分布式自动化测试平台", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")

@app.get("/health")
async def health(): return {"status": "ok", "db": "asyncmy", "queue": "redis"}

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)