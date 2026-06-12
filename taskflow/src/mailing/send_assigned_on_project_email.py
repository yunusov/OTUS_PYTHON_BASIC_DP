from .send_email import send_email
from src.core import settings
from src.models import UserOrm, ProjectOrm
from src.utils import templates


async def send_assigned_on_project_email(
    user: UserOrm,
    project: ProjectOrm,
):
    recipient = user.email
    subject = f"New assignment to project '{project.name}'"
    template = templates.get_template("mailing/project/email-assigned-on-project.txt")
    context = {
        "server_url": settings.SERVER_URL,
        "user": user,
        "project": project,
    }
    plain_content = template.render(context)
    template = templates.get_template("mailing/project/email-assigned-on-project.html")
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )
