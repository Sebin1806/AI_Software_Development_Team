from typing import Optional
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.orchestrator import AgentOrchestrator
from app.core.security import get_current_user
from app.database.database import SessionLocal, get_db
from app.database.models import AgentArtifact, AgentExecutionLog, Project, TaskExecution, User
from app.schemas.orchestrator import (
    AgentExecutionRequest,
    AgentExecutionResponse,
    StartTaskRequest,
    StartTaskResponse,
    TaskExecutionResultsResponse,
    TaskExecutionStatusResponse,
    WorkflowSummarySchema,
)

router = APIRouter()
orchestrator = AgentOrchestrator()


def run_orchestrator_background(task_id: UUID, mock_mode: Optional[bool] = None):
    """Background task runner using a dedicated DB session."""
    db = SessionLocal()
    try:
        orchestrator.execute_task(db, task_id, mock_mode=mock_mode)
    finally:
        db.close()


@router.get("/order")
def get_execution_order():
    return {
        "execution_order": orchestrator.get_execution_order()
    }


@router.post(
    "/next",
    response_model=AgentExecutionResponse
)
def get_next_agent(
    request: AgentExecutionRequest
):
    next_agent = orchestrator.get_next_agent(
        request.completed_agents
    )

    return {
        "next_agent": next_agent
    }


@router.post(
    "/start",
    response_model=StartTaskResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def start_software_task(
    request: StartTaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check project ownership
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or user unauthorized"
        )

    # Check for active running/pending task on same project
    existing_active_task = db.query(TaskExecution).filter(
        TaskExecution.project_id == request.project_id,
        TaskExecution.status.in_(["pending", "running"])
    ).first()

    if existing_active_task:
        return StartTaskResponse(
            task_id=existing_active_task.id,
            project_id=existing_active_task.project_id,
            status=existing_active_task.status,
            message="Active workflow task already in progress for this project."
        )

    task = TaskExecution(
        project_id=request.project_id,
        user_id=current_user.id,
        user_prompt=request.user_prompt,
        status="pending"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Launch execution asynchronously
    background_tasks.add_task(run_orchestrator_background, task.id)

    return StartTaskResponse(
        task_id=task.id,
        project_id=task.project_id,
        status="pending",
        message="Software development workflow started in background"
    )


@router.get(
    "/status/{task_id}",
    response_model=TaskExecutionStatusResponse
)
def get_task_status(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(TaskExecution).filter(
        TaskExecution.id == task_id,
        TaskExecution.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task execution not found"
        )

    logs = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.task_execution_id == task_id
    ).order_by(AgentExecutionLog.step_number.asc()).all()

    return TaskExecutionStatusResponse(
        task_id=task.id,
        project_id=task.project_id,
        status=task.status,
        current_step=task.current_step,
        total_steps=task.total_steps,
        percentage_completed=task.percentage_completed,
        current_agent=task.current_agent,
        agents_completed=task.agents_completed,
        agents_failed=task.agents_failed,
        artifacts_generated=task.artifacts_generated,
        created_at=task.created_at,
        completed_at=task.completed_at,
        logs=[
            {
                "agent_name": log.agent_name,
                "step_number": log.step_number,
                "status": log.status,
                "retry_count": log.retry_count,
                "started_at": log.started_at,
                "completed_at": log.completed_at,
                "error_message": log.error_message,
            }
            for log in logs
        ]
    )


@router.get(
    "/results/{task_id}",
    response_model=TaskExecutionResultsResponse
)
def get_task_results(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(TaskExecution).filter(
        TaskExecution.id == task_id,
        TaskExecution.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task execution not found"
        )

    logs = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.task_execution_id == task_id
    ).order_by(AgentExecutionLog.step_number.asc()).all()

    agent_outputs = {}
    code_review_findings = []
    security_findings = []
    generated_tests = []
    deployment_config = []

    for log in logs:
        if log.output_data:
            agent_outputs[log.agent_name] = log.output_data
            if log.agent_name == "Code Reviewer":
                code_review_findings = log.output_data.get("decisions", [])
            elif log.agent_name == "Security Engineer":
                security_findings = log.output_data.get("decisions", [])
            elif log.agent_name == "Test Engineer":
                generated_tests = log.output_data.get("deliverables", [])
            elif log.agent_name == "DevOps Engineer":
                deployment_config = log.output_data.get("deliverables", [])

    artifacts = db.query(AgentArtifact).filter(
        AgentArtifact.task_id == task_id
    ).order_by(AgentArtifact.created_at.asc()).all()

    summary = WorkflowSummarySchema(
        total_agents=task.total_steps,
        agents_completed=task.agents_completed,
        total_artifacts=len(artifacts),
        code_review_findings=code_review_findings,
        security_findings=security_findings,
        generated_tests=generated_tests,
        deployment_configuration=deployment_config,
        overall_status=task.status
    )

    return TaskExecutionResultsResponse(
        task_id=task.id,
        project_id=task.project_id,
        status=task.status,
        workflow_summary=summary,
        agent_outputs=agent_outputs,
        total_artifacts=len(artifacts),
        artifacts=[
            {
                "id": art.id,
                "task_id": art.task_id,
                "project_id": art.project_id,
                "agent_name": art.agent_name,
                "file_name": art.file_name,
                "relative_path": art.relative_path,
                "category": art.category,
                "file_type": art.file_type,
                "content": art.content,
                "version": art.version,
                "content_hash": art.content_hash,
                "created_at": art.created_at,
            }
            for art in artifacts
        ]
    )


@router.post(
    "/cancel/{task_id}"
)
def cancel_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(TaskExecution).filter(
        TaskExecution.id == task_id,
        TaskExecution.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task execution not found"
        )

    if task.status in ["completed", "failed", "cancelled"]:
        return {"task_id": task.id, "status": task.status, "message": f"Task is already {task.status}"}

    task.status = "cancelled"
    db.commit()

    return {"task_id": task.id, "status": "cancelled", "message": "Workflow cancellation requested successfully"}