from src.core.dependencies import ProjectRepo
from src.models import ProjectOrm
from src.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class ProjectService:
    def create(
        self,
        project_data: ProjectCreate,
        repository: ProjectRepo,
    ) -> ProjectRead:
        """Создание проекта"""
        project_orm = ProjectOrm(**project_data.model_dump())
        repository.create(project_orm)
        repository.save()
        return ProjectRead.model_validate(project_orm)

    def modify(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        repository: ProjectRepo,
    ) -> ProjectRead:
        """Изменение данных проекта"""
        project_orm = repository.get_by_id(project_id)
        if project_orm is None:
            raise ValueError("Проект с таким ID не существует!")

        project_orm.name = project_data.name
        project_orm.description = project_data.description
        project_orm.project_type = project_data.project_type
        project_orm.creator_id = project_data.creator_id

        repository.save()
        return ProjectRead.model_validate(project_orm)

    def delete(
        self,
        project_id: int,
        repository: ProjectRepo,
    ) -> bool:
        """Удаление проекта"""
        project_orm = repository.get_by_id(project_id)
        if project_orm is None:
            return False

        repository.delete(project_orm)
        repository.save()
        return True
