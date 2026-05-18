from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends

from src.core import database
from src.models import UserOrm

if TYPE_CHECKING:
    from src.core.async_session_wrapper import AsyncSessionWrapper


async def get_users_db(
    session: Annotated[
        "AsyncSessionWrapper",
        Depends(database.get_db_helper().get_session),
    ],
):
    yield UserOrm.get_db(session=session)
