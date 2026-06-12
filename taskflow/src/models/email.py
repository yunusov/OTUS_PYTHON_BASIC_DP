from typing import Optional

from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseOrm
from src.models.mixins import IntIdPkMixin, DateCreateUpdateMixin


class IncomingEmailOrm(
    BaseOrm,
    IntIdPkMixin,
    DateCreateUpdateMixin,
):
    __tablename__ = "tf_incoming_email"

    message_id:  Mapped[str] = mapped_column(Text, nullable=False)  # уникальный ID письма из заголовка
    from_email:  Mapped[str] = mapped_column(Text, nullable=False)
    subject:  Mapped[str] = mapped_column(Text, nullable=False)
    body_text:  Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed:  Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # обработано ли письмо
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # ошибка при обработке
