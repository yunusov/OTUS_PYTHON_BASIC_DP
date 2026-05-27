from .send_email import send_email
from src.models.user import UserOrm
from src.utils import templates


async def send_confirmed_email(
    user: UserOrm
):
    recipient = user.email
    subject = "Email confirmed for Taskflow"
    context = {
        "user": user
    }
    template = templates.get_template("mailing/email-verify/email-verified.txt")
    plain_content = template.render(context)

    template = templates.get_template("mailing/email-verify/email-verified.html")
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )
