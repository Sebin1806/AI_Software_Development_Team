from sqlalchemy.orm import Session

from app.database.models import Agent
from app.schemas.agent import AgentCreate


def create_agent(
    db: Session,
    project_id,
    agent_data: AgentCreate
):
    agent = Agent(
        project_id=project_id,
        name=agent_data.name,
        role=agent_data.role,
        status="idle"
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def get_project_agents(
    db: Session,
    project_id
):
    return (
        db.query(Agent)
        .filter(Agent.project_id == project_id)
        .order_by(Agent.created_at.asc())
        .all()
    )