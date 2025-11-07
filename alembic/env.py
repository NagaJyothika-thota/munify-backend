from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine, text

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- App-specific imports ---
from app.core.config import settings
from app.core.database import Base

# Auto-import all model modules under app.models so autogenerate can detect them
import importlib
import pkgutil
import app.models as models_pkg

for _, mod_name, _ in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module(f"{models_pkg.__name__}.{mod_name}")

# target metadata for autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    return (
        f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def ensure_database_exists(url: str) -> None:
    """Create target PostgreSQL database if it does not exist.

    This lets Alembic manage setup without separate scripts.
    """
    # Extract target DB name and build maintenance URL to 'postgres'
    from urllib.parse import urlparse

    parsed = urlparse(url)
    target_db = parsed.path.lstrip("/")
    maint_url = url.replace(f"/{target_db}", "/postgres")

    maint_engine = create_engine(maint_url)
    with maint_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target_db}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            conn.commit()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    ensure_database_exists(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    ensure_database_exists(get_url())
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=get_url(),
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
