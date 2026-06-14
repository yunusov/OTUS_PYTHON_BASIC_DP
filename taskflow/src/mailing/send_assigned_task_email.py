from .send_email import send_email
from src.core import settings
from src.models import UserOrm, TaskOrm
from src.utils import templates


async def send_assigned_task_email(
    user: UserOrm,
    task: TaskOrm,
):
    recipient = user.email
    subject = f"[Task-{task.id}] New task assignment '{task.name}'"
    template = templates.get_template("mailing/project/email-task-assigned.txt")
    context = {
        "server_url": settings.SERVER_URL,
        "user": user,
        "task": task,
    }
    plain_content = template.render(context)
    template = templates.get_template("mailing/project/email-task-assigned.html")
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )
