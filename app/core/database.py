import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_if_not_exists():
    try:
        conn = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (settings.DB_NAME,)
        )

        if not cursor.fetchone():
            try:
                cursor.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
                print(f"Database '{settings.DB_NAME}' created successfully.")
            except psycopg2.Error as db_err:
                if hasattr(db_err, "pgcode") and db_err.pgcode in ("42P04", "23505"):
                    print(
                        f"Database '{settings.DB_NAME}' was created concurrently by another worker."
                    )
                else:
                    raise
        else:
            print(f"Database '{settings.DB_NAME}' already exists.")

        cursor.close()
        conn.close()

    except Exception as e:
        err_msg = str(e).lower()
        if "already exists" in err_msg or "duplicate key" in err_msg:
            print(
                f"Database '{settings.DB_NAME}' already exists (handled during concurrent startup)."
            )
        else:
            print(f"Error while checking/creating database: {e}")
            raise
