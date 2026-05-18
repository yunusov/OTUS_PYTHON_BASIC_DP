import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any

from sqlalchemy import Result
from sqlalchemy.orm import Session


class AsyncSessionWrapper:
    """Обёртка синхронной SQLAlchemy Session,
    предоставляющая async-интерфейс,
    совместимый с fastapi_users_db_sqlalchemy.

    Быстрые операции (add) выполняются синхронно в текущем потоке.
    Тяжёлые операции (commit, refresh, execute и т.д.) — 
    в выделенном потоке для thread-safety.
    """

    def __init__(self, sync_session: Session):
        self._sync = sync_session
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def _run(self, fn, *args, **kwargs):
        """Выполнить функцию в выделенном потоке (max_workers=1)."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(fn, *args, **kwargs),
        )

    async def execute(self, statement: Any) -> Result:
        return await self._run(self._sync.execute, statement)

    async def commit(self) -> None:
        await self._run(self._sync.commit)

    async def rollback(self) -> None:
        await self._run(self._sync.rollback)

    async def close(self) -> None:
        await self._run(self._sync.close)

    async def refresh(self, instance: Any) -> None:
        await self._run(self._sync.refresh, instance)

    def add(self, instance: Any) -> None:
        """add — быстрая операция, выполняется синхронно."""
        self._sync.add(instance)

    async def delete(self, instance: Any) -> None:
        await self._run(self._sync.delete, instance)

    async def flush(self) -> None:
        await self._run(self._sync.flush)

    def get_sync_session(self) -> Session:
        """Доступ к оригинальной синхронной сессии, если нужно."""
        return self._sync
