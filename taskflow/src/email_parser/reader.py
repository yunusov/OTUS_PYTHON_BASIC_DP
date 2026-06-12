from src.core import settings
from src.schemas.email import Email
from src.utils import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()


def read_emails():
    """Read emails from email server"""
    admin_email = settings.email.email_login
    emails = get_emails(admin_email)

    if settings.run.EMAIL_REMOVE:
        for email in emails:
            remove_email(admin_email, email)

    return emails


def remove_email(admin_email, email):
    try:
        async_request(
            "DELETE",
            f"http://{settings.run.SERVER_IP}:9000/api/v1/mailbox/{admin_email}/{email["id"]}",
        )
    except Exception as e:
        logger.error(f"index failed: {e}")

def get_emails(admin_email):
    result = []
    try:
        result = async_request(
            "GET",
            f"{settings.EMAIL_SERVER_URL}{admin_email}",
        )
    except Exception as e:
        logger.error(f"get_emails failed: {e}")

    logger.info(f"get_emails {result=}")
    return result
