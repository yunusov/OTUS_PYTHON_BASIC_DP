from fastapi import APIRouter, Form, Query, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import TaskRepo
from src.schemas.user import UserRead
from src.services.task_service import TaskService
from src.utils.loguru_config import AppLogger
from src.utils.jinja_templates import templates


logger = AppLogger().get_logger()
router = APIRouter(prefix="/search")
ts = TaskService()


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    task_repository: TaskRepo,
    search_str: str = Query(""),
    tab: str = Query("tab"),
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc"),
    user: UserRead = Depends(get_current_user_from_session),
):
    # if search_str:
    tasks = ts.get_tasks_by_str(
        search_str,
        task_repository,
        sort_by,
        sort_dir,
    )
    context = {
        "request": request,
        "user": user,
        "page_title": "Задачи",
        "tasks": tasks,
        "search_str": search_str,
        "info": f"Задачи по запросу '{search_str}'",
        "no_found": f"По запросу '{search_str}' ничего не найдено.",
        "tab": "all",
        "current_sort": sort_by,
        "current_dir": sort_dir,
        "show_tab_mine": False,
    }
    return templates.TemplateResponse(
        request,
        "tasks/tasks_get.html",
        context,
    )


@router.post("/", response_class=HTMLResponse)
def search_post(
    request: Request,
    task_repository: TaskRepo,
    search_str: str = Form(""),
    tab: str = Query("tab"),
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc"),
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает список задач по поиску.
    """
    logger.info(f"Search string: {search_str}")
    if search_str:
        tasks = ts.get_tasks_by_str(
            search_str,
            task_repository,
            sort_by,
            sort_dir,
        )
        context = {
            "request": request,
            "user": user,
            "page_title": "Задачи",
            "tasks": tasks,
            "search_str": search_str,
            "info": f"Задачи по запросу '{search_str}'",
            "no_found": f"По запросу '{search_str}' ничего не найдено.",
            "tab": "all",
            "current_sort": sort_by,
            "current_dir": sort_dir,
            "show_tab_mine": False,
        }
        return templates.TemplateResponse(
            request,
            "tasks/tasks_get.html",
            context,
        )
    return RedirectResponse(url=request.url_for("index"), status_code=303)
