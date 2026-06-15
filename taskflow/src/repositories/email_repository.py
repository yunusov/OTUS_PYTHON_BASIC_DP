from sqlalchemy import and_, false, select

from .base import BaseRepository
from src.models.email import IncomingEmailOrm
from src.utils.loguru_config import AppLogger


logger = AppLogger().get_logger()

class EmailRepository(BaseRepository):
    
    def get_unprocessed_emails(self) -> list[IncomingEmailOrm]:
        result = self.session.execute(
            select(IncomingEmailOrm)
            .where(
                and_(
                    IncomingEmailOrm.error.is_(None),
                    IncomingEmailOrm.processed == false(),
                )
            )
        )
        return list(result.scalars().all())
