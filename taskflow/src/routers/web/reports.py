from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import TaskRepo, ProjectRepo, UserRepo
from src.schemas import UserRead, TaskStatus
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger
from datetime import datetime, timedelta
from collections import defaultdict

logger = AppLogger().get_logger()
router = APIRouter(prefix="/reports")


@router.get("/", response_class=HTMLResponse)
async def reports_index(
    request: Request,
    user: UserRead = Depends(get_current_user_from_session),
):
    """Главная страница отчетов"""
    context = {
        "request": request,
        "user": user,
        "page_title": "Отчеты",
    }
    return templates.TemplateResponse(request, "reports/index.html", context)


@router.get("/by-status", response_class=HTMLResponse)
async def report_by_status(
    request: Request,
    task_repository: TaskRepo,
    project_repository: ProjectRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отчет: Количество задач по статусам в разрезе проектов
    """
    # Получаем все проекты пользователя
    projects = project_repository.get_by_creator_id(user.id)

    # Подготавливаем данные
    statuses = [status.value for status in TaskStatus]
    projects_data = []

    # Считаем общую статистику для итоговой строки
    total_by_status = {status.value: 0 for status in TaskStatus}
    grand_total = 0

    for project in projects:
        # Получаем все задачи проекта
        tasks = task_repository.get_by_project(project.id, user_id=None)

        status_counts = {}
        for status in TaskStatus:
            count = sum(1 for t in tasks if t.status == status)
            status_counts[status.value] = count
            total_by_status[status.value] += count

        project_total = len(tasks)
        grand_total += project_total

        projects_data.append(
            {
                "id": project.id,
                "name": project.name,
                "status_counts": status_counts,
                "total": project_total,
            }
        )

    context = {
        "request": request,
        "user": user,
        "page_title": "Задачи по статусам",
        "projects": projects_data,
        "statuses": statuses,
        "total_by_status": total_by_status,
        "grand_total": grand_total,
    }
    return templates.TemplateResponse(request, "reports/by_status.html", context)


@router.get("/workload", response_class=HTMLResponse)
async def report_workload(
    request: Request,
    task_repository: TaskRepo,
    user_repository: UserRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отчет: Загрузка исполнителей
    """
    # Получаем всех пользователей
    users = user_repository.get_all()
    workload_data = []

    for u in users:
        # Используем ваш метод get_by_assignee
        tasks = task_repository.get_by_assignee(u.id)
        if not tasks:
            continue

        status_counts = {}
        for status in TaskStatus:
            count = sum(1 for t in tasks if t.status == status)
            if count > 0:
                status_counts[status.value] = count

        # Считаем просроченные задачи
        overdue_tasks = sum(
            1
            for t in tasks
            if t.due_date
            and t.due_date < datetime.now()
            and t.status != TaskStatus.DONE
        )

        workload_data.append(
            {
                "user_id": u.id,
                "user_name": u.fullname or u.username,
                "email": u.email,
                "total_tasks": len(tasks),
                "status_counts": status_counts,
                "overdue_tasks": overdue_tasks,
                "completion_rate": (
                    round(
                        sum(1 for t in tasks if t.status == TaskStatus.DONE)
                        / len(tasks)
                        * 100,
                        1,
                    )
                    if tasks
                    else 0
                ),
            }
        )

    # Сортируем по количеству задач (по убыванию)
    workload_data.sort(key=lambda x: x["total_tasks"], reverse=True)

    context = {
        "request": request,
        "user": user,
        "page_title": "Загрузка исполнителей",
        "data": workload_data,
        "total_assignees": len(workload_data),
    }
    return templates.TemplateResponse(request, "reports/workload.html", context)


@router.get("/completion-time", response_class=HTMLResponse)
async def report_completion_time(
    request: Request,
    task_repository: TaskRepo,
    user: UserRead = Depends(get_current_user_from_session),
    days_back: int = Query(30, ge=1, le=365),
):
    """
    Отчет: Среднее время выполнения задачи
    Используем created_at и updated_at из модели
    """
    cutoff_date = datetime.now() - timedelta(days=days_back)

    # Получаем все задачи пользователя
    all_tasks = task_repository.get_by_user(user.id)

    # Фильтруем завершенные задачи за указанный период
    # Используем updated_at как дату завершения (когда статус стал DONE)
    completed_tasks = [
        t
        for t in all_tasks
        if t.status == TaskStatus.DONE
        and t.updated_at  # дата последнего обновления
        and t.updated_at >= cutoff_date
        and t.created_at  # дата создания
    ]

    if not completed_tasks:
        context = {
            "request": request,
            "user": user,
            "page_title": "Среднее время выполнения",
            "message": f"Нет завершенных задач за последние {days_back} дней",
            "days_back": days_back,
            "data": None,
        }
        return templates.TemplateResponse(
            request, "reports/completion_time.html", context
        )

    # Общая статистика
    total_tasks = len(completed_tasks)
    total_hours = sum(
        (t.updated_at - t.created_at).total_seconds() / 3600
        for t in completed_tasks
        if t.updated_at and t.created_at
    )
    overall_average = total_hours / total_tasks if total_tasks > 0 else 0

    # Статистика по проектам
    projects_stats = defaultdict(lambda: {"tasks": [], "total_hours": 0})
    for task in completed_tasks:
        project_name = task.project.name if task.project else "Без проекта"
        time_hours = (task.updated_at - task.created_at).total_seconds() / 3600
        projects_stats[project_name]["tasks"].append(time_hours)
        projects_stats[project_name]["total_hours"] += time_hours

    by_project = []
    for project_name, stats in projects_stats.items():
        avg = stats["total_hours"] / len(stats["tasks"]) if stats["tasks"] else 0
        by_project.append(
            {
                "project_name": project_name,
                "average_hours": round(avg, 2),
                "tasks_count": len(stats["tasks"]),
            }
        )
    by_project.sort(key=lambda x: x["average_hours"])

    # Статистика по исполнителям
    assignees_stats = defaultdict(lambda: {"tasks": [], "total_hours": 0})
    for task in completed_tasks:
        assignee_name = task.assignee.fullname if task.assignee else "Неизвестный"
        time_hours = (task.updated_at - task.created_at).total_seconds() / 3600
        assignees_stats[assignee_name]["tasks"].append(time_hours)
        assignees_stats[assignee_name]["total_hours"] += time_hours

    by_assignee = []
    for assignee_name, stats in assignees_stats.items():
        avg = stats["total_hours"] / len(stats["tasks"]) if stats["tasks"] else 0
        by_assignee.append(
            {
                "assignee_name": assignee_name,
                "average_hours": round(avg, 2),
                "tasks_count": len(stats["tasks"]),
            }
        )
    by_assignee.sort(key=lambda x: x["average_hours"])

    context = {
        "request": request,
        "user": user,
        "page_title": "Среднее время выполнения",
        "data": {
            "period_days": days_back,
            "total_tasks": total_tasks,
            "overall_average": round(overall_average, 2),
            "by_project": by_project,
            "by_assignee": by_assignee,
        },
        "days_back": days_back,
        "message": None,
    }
    return templates.TemplateResponse(request, "reports/completion_time.html", context)


@router.get("/dashboard", response_class=HTMLResponse)
async def report_dashboard(
    request: Request,
    task_repository: TaskRepo,
    project_repository: ProjectRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Дашборд со сводной информацией
    """
    # Получаем все задачи пользователя
    tasks = task_repository.get_by_user(user.id)
    projects = project_repository.get_by_creator_id(user.id)

    # Статистика по статусам
    status_summary = {}
    for status in TaskStatus:
        count = sum(1 for t in tasks if t.status == status)
        status_summary[status.value] = count

    # Просроченные задачи
    overdue_tasks = sum(
        1
        for t in tasks
        if t.due_date and t.due_date < datetime.now() and t.status != TaskStatus.DONE
    )

    # Процент выполнения
    completion_rate = (
        sum(1 for t in tasks if t.status == TaskStatus.DONE) / len(tasks) * 100
        if tasks
        else 0
    )

    context = {
        "request": request,
        "user": user,
        "page_title": "Сводка",
        "data": {
            "total_tasks": len(tasks),
            "total_projects": len(projects),
            "overdue_tasks": overdue_tasks,
            "completion_rate": round(completion_rate, 1),
            "status_summary": status_summary,
        },
    }
    return templates.TemplateResponse(request, "reports/dashboard.html", context)
