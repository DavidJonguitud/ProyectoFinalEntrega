import pytest
from typing import Generator, AsyncGenerator
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import httpx
from httpx import AsyncClient
from unittest.mock import MagicMock

import boto3
import os

from app.core.config import Settings, settings
from app.main import app
from app.core.database import Base, get_db  
from app.core.security import create_access_token, hash_password
from app.models.user import User
from moto import mock_aws

TEST_DB_NAME = "test_database"
TEST_BUCKET = "test-project-bucket-ficticio"
TEST_FOLDER = "project_99"


db_url_parts = settings.DATABASE_URL.split("/")
db_url_parts[-1] = TEST_DB_NAME
TEST_DATABASE_URL = "/".join(db_url_parts)

def create_database_if_not_exists():
    try:
        conn = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database="postgres"  
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,)
        )

        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE {TEST_DB_NAME}')
            print(f"\n[TESTING] Base de datos '{TEST_DB_NAME}' creada con éxito.")
        else:
            print(f"\n[TESTING] Base de datos '{TEST_DB_NAME}' ya existe.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n[TESTING] Error al verificar/crear la base de datos: {e}")
        raise

create_database_if_not_exists()

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
async def client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session: Session) -> User:

    hashed_pass = hash_password("bla")
    user = User(
        email="test_user@example.com",
        hashed_password= hashed_pass
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    access_token = create_access_token(subject=test_user.email)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def mock_s3_env(monkeypatch):
    with mock_aws():
        mocked_client = boto3.client("s3", region_name="us-east-1")
        
        mocked_client.create_bucket(Bucket="test-project-bucket-ficticio")
        
        monkeypatch.setattr(Settings, "s3_client", mocked_client)
        
        yield mocked_client