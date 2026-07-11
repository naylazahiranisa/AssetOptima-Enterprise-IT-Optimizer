"""Alembic environment configuration.

Loads the SQLAlchemy Base metadata for auto-detection of models
and reads the database URL from application settings so migrations
stay in sync with the runtime configuration.
"""

from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config

from alembic import context

from app.config.settings import settings
from app.database.base import Base

# Alembic Config object
config = context.config

# Override the database URL from settings (sync variant for Alembic)
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Set up Python loggers from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode (SQL script generation)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode (connect to live database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
