from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import Session, sessionmaker

from rootski.config.config import Config
from rootski.services.service import Service


class DBService(Service):
    def __init__(self, sync_db_uri: str, async_db_uri: str):
        self.sync_db_uri = sync_db_uri
        self.async_db_uri = async_db_uri

    @classmethod
    def from_config(cls: Type[DBService], config: Config) -> DBService:
        return cls(
            sync_db_uri=str(config.sync_sqlalchemy_database_uri),
            async_db_uri=str(config.async_sqlalchemy_database_uri),
        )

    def init(self):
        """Ping the database to validate the connection parameters.

        :raises Exception: if fails to ping the database."""
        self.sync_engine: Engine = create_engine(
            self.sync_db_uri,
            pool_pre_ping=True,
            # echo=True,
            # connect_args={"connect_timeout": 5}
        )
        self.sync_sessionmaker: sessionmaker = sessionmaker(
            autocommit=False, autoflush=False, bind=self.sync_engine
        )

        self.async_engine: AsyncEngine = create_async_engine(
            self.async_db_uri,
            future=True,
            pool_size=20,  # TODO - what is this?
        )
        self.async_sessionmaker: sessionmaker = sessionmaker(
            future=True, class_=AsyncSession, bind=self.async_engine
        )

        # TODO - should this healthcheck go in a request dependency instead? That way
        # this logic wouldn't run when requesting the /docs page and other things.
        # health check the database
        # with self.sync_engine.connect() as conn:
        #     result: Result = conn.execute("SELECT 1")
        #     data = result.scalars().one()
        #     logger.info(f'DBService got "{str(data)}" back after running "SELECT 1" on the database.')

    def get_sync_session(self) -> Session:
        return self.sync_sessionmaker()

    @asynccontextmanager
    async def get_async_session(self) -> Session:
        session: AsyncSession
        async with self.async_sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
