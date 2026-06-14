import asyncio

import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core import settings
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


async def send_email(
    recipient: str,
    subject: str,
    plain_content: str,
    html_content: str = "",
):
    admin_email = settings.email.email_login

    message = MIMEMultipart("alternative")
    message["From"] = admin_email
    message["To"] = recipient
    message["Subject"] = subject
    logger.info(
        "Sending email to '{}' with subject '{}'",
        recipient,
        subject,
    )

    plain_text_message = MIMEText(
        plain_content,
        "plain",
        "utf-8",
    )
    message.attach(plain_text_message)

    if html_content:
        html_message = MIMEText(
            html_content,
            "html",
            "utf-8",
        )
        message.attach(html_message)

    try:
        async with aiosmtplib.SMTP(
            hostname=settings.email.email_host,
            port=int(settings.email.email_port),
        ) as smtp:
            #  await smtp.starttls()  # Явное переключение на TLS
            if settings.email.smtp_auth:
                await smtp.login(
                    settings.email.email_login,
                    settings.email.email_token
                )
            await smtp.send_message(message)
    except aiosmtplib.SMTPAuthenticationError:
        logger.error("SMTP: Неверные учётные данные")
    except aiosmtplib.SMTPConnectError as e:
        logger.error("SMTP: Ошибка подключения к серверу: %s", e)
    except aiosmtplib.SMTPResponseException as e:
        logger.error("SMTP: Сервер вернул ошибку %d: %s", e.code, e.message)
    except asyncio.TimeoutError:
        logger.error("SMTP: Таймаут подключения")
    except OSError as e:
        logger.error("SMTP: Сетевая ошибка: %s", e)
    except Exception as e:
        logger.exception("SMTP: Неожиданная ошибка: %s", e)
