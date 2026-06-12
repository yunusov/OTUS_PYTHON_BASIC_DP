from fastapi import Depends

from src.core.auth.user_manager import UserManager
from src.core.dependencies import ProjectRepo
from src.models import ProjectOrm, UserProjectOrm, UserOrm
from src.routers.api.dependencies.auth.user_manager import get_user_manager
from src.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectMembersAdd,
)
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class ProjectService:

    def create(
        self,
        project_data: ProjectCreate,
        repository: ProjectRepo,
    ) -> ProjectRead:
        project_orm = ProjectOrm(**project_data.model_dump())
        creator = repository.session.get(UserOrm, project_data.creator_id)

        if creator is None:
            raise ValueError("Пользователь-создатель не найден")

        project_orm.user_projects.append(UserProjectOrm(user=creator))
        repository.create(project_orm)
        repository.save()
        return ProjectRead.model_validate(project_orm)

    async def add_members(
        self,
        project_id: int,
        data: ProjectMembersAdd,
        repository: ProjectRepo,
        user_manager: UserManager,
    ) -> ProjectRead:
        project_orm = repository.get_by_id(project_id)
        if project_orm is None:
            raise ValueError("Проект с таким ID не существует!")

        existing_user_ids = {link.user_id for link in project_orm.user_projects}
        new_user_ids = [
            user_id for user_id in data.user_ids if user_id not in existing_user_ids
        ]
        removed_user_ids = existing_user_ids - set(data.user_ids)
        if removed_user_ids:
            repository.remove_members(project_id, removed_user_ids)

        if not new_user_ids:
            repository.save()
            return ProjectRead.model_validate(project_orm)

        users = (
            repository.session.query(UserOrm).filter(UserOrm.id.in_(new_user_ids)).all()
        )
        found_user_ids = {user.id for user in users}

        missing_user_ids = set(new_user_ids) - found_user_ids
        if missing_user_ids:
            raise ValueError(f"Пользователи с ID={sorted(missing_user_ids)} не найдены")

        await self.user_projects_extend(project_orm, users, user_manager)

        repository.save()
        return ProjectRead.model_validate(project_orm)

    def modify(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        repository: ProjectRepo,
    ) -> ProjectRead:
        project_orm = repository.get_by_id(project_id)
        if project_orm is None:
            raise ValueError("Проект с таким ID не существует!")

        if project_data.name is not None:
            project_orm.name = project_data.name
        if project_data.description is not None:
            project_orm.description = project_data.description
        if project_data.project_type is not None:
            project_orm.project_type = project_data.project_type

        if project_data.creator_id is not None:
            new_creator = repository.session.get(UserOrm, project_data.creator_id)
            if new_creator is None:
                raise ValueError("Пользователь-создатель не найден")

            project_orm.creator_id = project_data.creator_id

            existing_user_ids = {link.user_id for link in project_orm.user_projects}
            if project_data.creator_id not in existing_user_ids:
                project_orm.user_projects.append(UserProjectOrm(user=new_creator))

        repository.save()
        return ProjectRead.model_validate(project_orm)

    def delete(
        self,
        project_id: int,
        repository: ProjectRepo,
    ) -> bool:
        project_orm = repository.get_by_id(project_id)
        if project_orm is None:
            return False

        repository.delete(project_orm)
        repository.save()
        return True

    def get_by_creator_id(
        self,
        repository: ProjectRepo,
        owner_id: int | None = None,
        sort_by: str = "name",
        sort_dir: str = "desc",
    ) -> list[ProjectRead]:
        projects = repository.get_by_creator_id(owner_id)
        result = [
            ProjectRead.model_validate(project, from_attributes=True).model_copy(
                update={"owner": project.creator.fullname}
            )
            for project in projects
        ]
        sort_map = {
            "name": lambda p: p.name.lower(),
            "owner": lambda p: p.owner.lower(),
            "project_type": lambda p: p.project_type,
            "created_at": lambda p: p.created_at,
        }
        key_func = sort_map[sort_by]
        result.sort(key=key_func, reverse=(sort_dir == "desc"))
        return result

    def get_by_id(
        self,
        project_id: int,
        repository: ProjectRepo,
    ) -> ProjectRead:
        project = repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Проект с таким ID не существует!")

        return ProjectRead.model_validate(project, from_attributes=True).model_copy(
            update={"owner": project.creator.fullname}
        )

    async def user_projects_extend(
        self,
        project: ProjectOrm | None,
        users: list[UserOrm],
        user_manager: UserManager,
    ):
        if project:
            project.user_projects.extend(UserProjectOrm(user=user) for user in users)
            await user_manager.on_project_assign(users, project)
