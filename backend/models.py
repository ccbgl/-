from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "user"), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    tasks = relationship("TestTask", back_populates="creator")

class TestTask(Base):
    __tablename__ = "test_tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    repo_url = Column(String(255), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    creator = relationship("User", back_populates="tasks")
    plans = relationship("TestPlan", back_populates="task", cascade="all, delete-orphan")

class TestPlan(Base):
    __tablename__ = "test_plans"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"))
    name = Column(String(100), nullable=False)
    plan_type = Column(Enum("full", "suite", "scheduled"), default="full")
    cron_expr = Column(String(50), nullable=True)
    status = Column(Enum("inactive", "active"), default="inactive")
    created_at = Column(DateTime, default=datetime.utcnow)
    task = relationship("TestTask", back_populates="plans")
    executions = relationship("Execution", back_populates="plan", cascade="all, delete-orphan")

class Execution(Base):
    __tablename__ = "executions"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("test_plans.id"))
    status = Column(Enum("pending", "running", "success", "failed"), default="pending")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    report_url = Column(String(255), nullable=True)
    logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    plan = relationship("TestPlan", back_populates="executions")