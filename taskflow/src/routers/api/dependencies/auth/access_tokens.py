from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends

from src.core import database
from src.models import AccessTokenOrm

if TYPE_CHECKING:
    from src.core.async_session_wrapper import AsyncSessionWrapper


async def get_access_tokens_db(
    session: Annotated[
        "AsyncSessionWrapper",
        Depends(database.get_db_helper().get_session),
    ],
):
    yield AccessTokenOrm.get_db(session=session)
