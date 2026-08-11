from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import AgentArtifact, Project, TaskExecution, User
from app.schemas.orchestrator import ArtifactSchema

router = APIRouter()


@router.get(
    "/projects/{project_id}/artifacts",
    response_model=list[ArtifactSchema]
)
def list_project_artifacts(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    artifacts = db.query(AgentArtifact).filter(
        AgentArtifact.project_id == project_id
    ).order_by(AgentArtifact.created_at.desc()).all()

    return artifacts


@router.get(
    "/orchestrator/results/{task_id}/artifacts",
    response_model=list[ArtifactSchema]
)
def list_task_artifacts(
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
            detail="Task execution not found or unauthorized"
        )

    artifacts = db.query(AgentArtifact).filter(
        AgentArtifact.task_id == task_id
    ).order_by(AgentArtifact.created_at.asc()).all()

    return artifacts


@router.get(
    "/projects/{project_id}/artifacts/{artifact_id}",
    response_model=ArtifactSchema
)
def get_single_artifact(
    project_id: UUID,
    artifact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    artifact = db.query(AgentArtifact).filter(
        AgentArtifact.id == artifact_id,
        AgentArtifact.project_id == project_id
    ).first()

    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found"
        )

    return artifact


@router.get(
    "/projects/{project_id}/artifacts/{artifact_id}/download"
)
def download_artifact(
    project_id: UUID,
    artifact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    artifact = db.query(AgentArtifact).filter(
        AgentArtifact.id == artifact_id,
        AgentArtifact.project_id == project_id
    ).first()

    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found"
        )

    media_type = "text/plain"
    if artifact.file_type in ["json", "yaml", "sql", "md", "py", "js", "ts", "tsx"]:
        media_type = f"application/{artifact.file_type}"

    headers = {
        "Content-Disposition": f'attachment; filename="{artifact.file_name}"'
    }

    return Response(
        content=artifact.content,
        media_type=media_type,
        headers=headers
    )
