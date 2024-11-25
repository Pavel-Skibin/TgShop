from functools import wraps
from os import environ

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


class Base:
    __allow_unmapped__ = True

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()


Base = declarative_base(cls=Base)

env = environ.get

__factory = None


def get_database_url(alembic: bool = False) -> str:
    schema = "postgresql+asyncpg"

    if alembic:
        schema = "postgresql"

    return (f"{schema}://{env('db_login')}:{env('db_password')}@"
            f"{env('db_host')}:{env('db_port')}/{env('db_name')}")


async def global_init():
    global __factory

    if __factory:
        return
    conn_str = get_database_url()

    engine = create_async_engine(conn_str, pool_pre_ping=True)

    async with engine.begin() as conn:
        # await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    __factory = async_sessionmaker(
        engine, expire_on_commit=False
    )
    from . import __all_models  # noqa


def create_session() -> AsyncSession:
    global __factory
    return __factory()  # noqa


def session_db(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with create_session() as session:
            return await func(*args, session=session, **kwargs)

    return wrapper