import re

from src.core.database import get_db_helper
from src.repositories import CommentRepository, EmailRepository, TaskRepository
from src.schemas import TaskStatus
from src.utils import AppLogger
from taskflow.src.schemas.comment import CommentCreate


logger = AppLogger().get_logger()
db_helper = get_db_helper()

def process_emails():
    with db_helper.session_factory() as session:
        emailRepository = EmailRepository(session)
        taskRepository = TaskRepository(session)
        commentRepository = CommentRepository(session)
        emails = emailRepository.get_unprocessed_emails()
        for email in emails:
            process_task_status(email, emailRepository, taskRepository)
            add_comment(email, emailRepository, commentRepository) # add


        emailRepository.save()
        taskRepository.save()

def add_comment(email, emailRepository, commentRepository):
    task_id = extract_task_id(email.subject)
    creator_email = email.from_email
    if task_id:
        email_body = email.body
        if email_body:
            try:
                comment = CommentCreate(content=email_body, task_id=task_id, creator_id=123)
                commentRepository.add_comment(comment)
                
            except Exception as e:
                emailRepository.update_email_error(email, f"FAILED: {e}")


def process_task_status(email, emailRepository, taskRepository):
    task_id = extract_task_id(email.subject)
    if extract_body_inp(email.body):
        try:
            if task_id:
                task = taskRepository.get_by_id(task_id)
                if task.assignee.email == email.from_email:
                    taskRepository.update_task_status(task, TaskStatus.IN_PROGRESS)
                else:
                    emailRepository.update_email_error(email, "Email does not match with assignee!")
        except Exception as e:
            emailRepository.update_email_error(email, f"FAILED: {e}")

def extract_task_id(subject: str) -> str | None:
    match = re.search(r"\[Task-(\d+)\]", subject)
    return match.group(1) if match else None

def extract_body_inp(body: str) -> bool:
    match = re.search(r"\*+inp\*", body)
    return True if match else False