"""Exception module: custom exception classes and global error handlers."""

from app.exceptions.handlers import register_exception_handlers

__all__ = ["register_exception_handlers"]
