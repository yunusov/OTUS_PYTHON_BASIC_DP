from src.core import settings
from src.core.database import get_db_helper
from src.repositories.email_repository import EmailRepository
from src.models import IncomingEmailOrm
from src.schemas.email import Email
from src.utils import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()
db_helper = get_db_helper()


def parse_emails(emails):
    """Parse emails from email server."""
    admin_email = settings.email.email_login
    with db_helper.session_factory() as session:
        emailRepository = EmailRepository(session)
        try:
            for email in emails:
                body = get_email_body_text(admin_email, email)
                email = Email(
                    message_id=email["id"],
                    from_email=email["from"],
                    subject=email["subject"],
                    body_text=body,
                    body_html=None,
                    processed=False,
                    error=None,
                )
                email = IncomingEmailOrm(**email.model_dump())
        except Exception as e:
            logger.exception(f"Ошибка: {e}")     
    emailRepository.save()


def get_email_body_text(admin_email, email):
    response = {}
    result = ""
    try:
        response = async_request(
            "GET",
            f"{settings.EMAIL_SERVER_URL}{admin_email}/{email["id"]}",
        )
    except Exception as e:
        logger.error(f"get_email_body failed: {e}")

    if response:
        result = response["body"]["text"]

    logger.info(f"get_email_body {result=}")
    return result
