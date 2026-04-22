import datetime

from sqlalchemy import func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class DateCreateUpdateMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=lambda *args: datetime.datetime.now(datetime.UTC),
    )
