from sqlalchemy.orm import Session

from app.database.models import Project
from app.schemas.project import ProjectCreate


def create_project(
    db: Session,
    project_data: ProjectCreate,
    owner_id
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=owner_id,
        status="planning"
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_user_projects(
    db: Session,
    owner_id
):
    return (
        db.query(Project)
        .filter(Project.owner_id == owner_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project(
    db: Session,
    project_id,
    owner_id
):
    return (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == owner_id
        )
        .first()
    )


def delete_project(
    db: Session,
    project_id,
    owner_id
):
    project = get_project(
        db,
        project_id,
        owner_id
    )

    if project is None:
        return False

    db.delete(project)
    db.commit()

    return True