from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.utils.loguru_config import AppLogger
from src.core.dependencies import DbSession
from src.repositories.task_repository import TaskRepository
from src.schemas.task import TaskInDB, Task
from src.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = AppLogger().get_logger()

def get_task_repo(session: Session = Depends(DbSession)):
    return TaskRepository(session)

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskInDB,
    repo: TaskRepository = Depends(get_task_repo)
) -> Task:
    service = TaskService(repo)
    try:
        return service.create(task)
    except IntegrityError:
        raise HTTPException(400, "project_id/creator_id/assignee_id не существует")

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, repo: TaskRepository = Depends(get_task_repo)) -> Task:
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return Task.model_validate(task)

@router.get("/", response_model=list[Task])
def get_tasks(project_id: int, repo: TaskRepository = Depends(get_task_repo)) -> list[Task]:
    tasks = repo.get_by_project_id(project_id)
    return [Task.model_validate(t) for t in tasks]

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskInDB, repo: TaskRepository = Depends(get_task_repo)) -> Task:
    task_data.id = task_id
    service = TaskService(repo)
    return service.modify(task_data)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, repo: TaskRepository = Depends(get_task_repo)) -> None:
    service = TaskService(repo)
    if not service.delete(task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")