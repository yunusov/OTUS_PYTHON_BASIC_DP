from .send_email import send_email
from src.core import settings
from src.models import UserOrm, CommentOrm, TaskOrm
from src.utils import templates


async def send_comment_email(
    user: UserOrm,
    task: TaskOrm,
    comment: CommentOrm,
):
    recipient = user.email
    subject = f"[Task-{task.id}] New reply on task {task.name}"
    template = templates.get_template("mailing/project/email-comment.txt")
    context = {
        "server_url": settings.SERVER_URL,
        "user": user,
        "comment": comment,
        "task": task,
    }
    plain_content = template.render(context)
    template = templates.get_template("mailing/project/email-comment.html")
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )
