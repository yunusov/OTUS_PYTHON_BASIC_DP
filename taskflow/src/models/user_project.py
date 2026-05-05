from sqlalchemy import Table, Column, Integer, ForeignKey

from src.core.database import BaseOrm

user_project = Table(
    "tf_user_project",
    BaseOrm.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("tf_users.id"), nullable=False),
    Column("project_id", Integer, ForeignKey("tf_projects.id"), nullable=False),
)