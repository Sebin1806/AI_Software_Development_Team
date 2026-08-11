from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(150), nullable=False)

    description = Column(Text, nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="planning"
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    role = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="idle"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_prompt = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed, cancelled
    current_agent = Column(String(100), nullable=True)
    current_step = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=12)
    percentage_completed = Column(Integer, nullable=False, default=0)
    agents_completed = Column(Integer, nullable=False, default=0)
    agents_failed = Column(Integer, nullable=False, default=0)
    artifacts_generated = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_execution_id = Column(UUID(as_uuid=True), ForeignKey("task_executions.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    step_number = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed, retrying, skipped
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AgentArtifact(Base):
    __tablename__ = "agent_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("task_executions.id"), nullable=False)
    task_execution_id = Column(UUID(as_uuid=True), ForeignKey("task_executions.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    relative_path = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False, default="docs")
    file_type = Column(String(50), nullable=False)  # code, markdown, sql, json, yaml, dockerfile, txt
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
