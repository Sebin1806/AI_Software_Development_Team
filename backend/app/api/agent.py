from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.schemas.agent import AgentCreate, AgentResponse
from app.services.agent_service import (
    create_agent,
    get_project_agents,
)
from app.services.project_service import get_project


router = APIRouter()


@router.post(
    "/{project_id}",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_agent(
    project_id: UUID,
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Make sure the project belongs to the logged-in user
    project = get_project(
        db,
        project_id,
        current_user.id
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return create_agent(
        db,
        project_id,
        agent_data
    )


@router.get(
    "/{project_id}",
    response_model=list[AgentResponse]
)
def list_agents(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(
        db,
        project_id,
        current_user.id
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return get_project_agents(
        db,
        project_id
    )