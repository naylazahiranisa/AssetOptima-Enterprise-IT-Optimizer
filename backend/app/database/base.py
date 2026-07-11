"""Declarative base for SQLAlchemy ORM models.

All domain models inherit from this single Base instance,
enabling Alembic to discover them automatically.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
