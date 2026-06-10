from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse

from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import TaskRepo
from src.schemas.user import UserRead
from src.services.task_service import TaskService
from src.utils.loguru_config import AppLogger
from src.utils.jinja_templates import templates


logger = AppLogger().get_logger()
router = APIRouter(prefix="/search")
ts = TaskService()

@router.post("/", response_class=HTMLResponse)
def index(
    request: Request,
    task_repository: TaskRepo,
    search_str: str = Form(""),
    user: UserRead = Depends(get_current_user_from_session),
):
    """
        Отображает список задач по поиску.
    """
    logger.info(f"Search string: {search_str}")
    if search_str:
        tasks = ts.get_tasks_by_str(search_str, task_repository)
        context = {
            "request": request,
            "user": user,
            "page_title": "Задачи",
            "tasks": tasks,
            "info": f"Задачи по запросу '{search_str}'",
            "no_found": f"По запросу '{search_str}' ничего не найдено.",
        }
        return templates.TemplateResponse(
            request,
            "tasks/tasks_get.html",
            context,
        )