from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum): admin = "admin"; user = "user"
class PlanType(str, Enum): full = "full"; suite = "suite"; scheduled = "scheduled"
class ExecStatus(str, Enum): pending = "pending"; running = "running"; success = "success"; failed = "failed"

class UserLogin(BaseModel): username: str; password: str
class UserCreate(BaseModel): username: str = Field(..., min_length=3); password: str = Field(..., min_length=6); role: UserRole = UserRole.user
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class UserResponse(BaseModel): id: int; username: str; role: UserRole; created_at: datetime; model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel): name: str; description: Optional[str] = ""; repo_url: Optional[str] = None
class TaskResponse(BaseModel): id: int; name: str; description: str; repo_url: str; creator_id: int; created_at: datetime; model_config = ConfigDict(from_attributes=True)

class PlanCreate(BaseModel): name: str; plan_type: PlanType = PlanType.full; cron_expr: Optional[str] = None
class PlanResponse(BaseModel): id: int; task_id: int; name: str; plan_type: PlanType; cron_expr: Optional[str]; status: str; created_at: datetime; model_config = ConfigDict(from_attributes=True)

class ExecutionResponse(BaseModel): id: int; plan_id: int; status: ExecStatus; start_time: Optional[datetime]; end_time: Optional[datetime]; report_url: Optional[str]; logs: Optional[str]; created_at: datetime; model_config = ConfigDict(from_attributes=True)