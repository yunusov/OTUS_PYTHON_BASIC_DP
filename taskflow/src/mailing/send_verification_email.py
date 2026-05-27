from .send_email import send_email
from src.models.user import UserOrm
from src.utils import templates


async def send_verification_email(
    user: UserOrm,
    verification_link: str,
    verification_token: str,
):
    recipient = user.email
    subject = "Verify your email for Taskflow"
    template = templates.get_template("mailing/email-verify/verification-request.txt")
    context = {
        "user": user,
        "verification_link": verification_link,
        "verification_token": verification_token,
    }
    plain_content = template.render(context)
    template = templates.get_template("mailing/email-verify/verification-request.html")
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )
