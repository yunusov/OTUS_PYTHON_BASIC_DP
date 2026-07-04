from apscheduler.schedulers.background import BackgroundScheduler

from .reader import read_emails
from .parser import parse_emails
from src.core import settings
from src.utils import AppLogger

logger = AppLogger().get_logger()


class EmailScheduler:
    def process_emails(self):
        # logger.info("Task is running")
        email_scheduler = settings.email.email_scheduler
        if email_scheduler:
            emails = read_emails()
            parse_emails(emails)

    def start(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.process_emails,
            "interval",
            seconds=settings.run.EMAIL_SCHEDULER_INTERVAL,
        )
        scheduler.start()
