from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.src.models.project import ProjectOrm
from taskflow.src.schemas.project import Project, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> ProjectOrm:
        project_orm = ProjectOrm(**project.model_dump())
        self.session.add(project_orm)
        self.session.commit()
        self.session.refresh(project_orm)
        return project_orm

    def get_by_id(self, project_id: int) -> ProjectOrm | None:
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.id == project_id)
        )
        return result.scalar_one_or_none()

    def get_by_creator(self, creator_id: int) -> list[ProjectOrm]:
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.creator_id == creator_id)
        )
        return list(result.scalars().all())

    def get_by_type(self, project_type: str) -> list[ProjectOrm]:
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.project_type == project_type)
        )
        return list(result.scalars().all())

    def update(self, project_id: int, project_data: ProjectUpdate) -> ProjectOrm | None:
        project = self.get_by_id(project_id)

        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: int | None) -> bool:
        if not project_id:
            return False
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.session.delete(project)
        self.session.commit()
        return True