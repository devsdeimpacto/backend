from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from app.settings import Settings

Base = declarative_base() ##necessário para os modelos SQLAlchemy herdarem de uma classe base declarativa.

settings = Settings()
# Converte postgres:// ou postgresql:// para postgresql+psycopg://
# para usar psycopg3 ao invés de psycopg2
database_url = settings.DATABASE_URL
if database_url.startswith('postgres://'):
    database_url = database_url.replace(
        'postgres://', 'postgresql+psycopg://', 1
    )
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace(
        'postgresql://', 'postgresql+psycopg://', 1
    )
engine = create_engine(database_url)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
