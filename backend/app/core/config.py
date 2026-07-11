"""Backward-compatible re-export of application settings.

Prefer importing directly from ``app.config.settings`` in new code.
"""

from app.config.settings import settings  # noqa: F401
