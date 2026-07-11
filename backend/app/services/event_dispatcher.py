"""Event dispatcher that coordinates notifications and audit logging.

Central entry point for raising domain events from any service.
Automatically creates audit logs and notifications based on event type.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.notification import Notification, NotificationCategory, NotificationPriority, NotificationStatus

logger = logging.getLogger(__name__)


# ── Provider Interfaces (real-time ready) ──────────────────────────

class NotificationProvider(ABC):
    """Interface for notification delivery channels."""

    @abstractmethod
    async def send(self, notification: dict[str, Any]) -> bool:
        """Deliver a notification through this channel. Return True on success."""
        ...


class WebSocketProvider(NotificationProvider):
    """Placeholder for WebSocket push (not yet implemented)."""

    async def send(self, notification: dict[str, Any]) -> bool:
        logger.debug("WebSocketProvider.send not yet implemented: %s", notification.get("id"))
        return False


class FirebaseCloudMessagingProvider(NotificationProvider):
    """Placeholder for Firebase Cloud Messaging (not yet implemented)."""

    async def send(self, notification: dict[str, Any]) -> bool:
        logger.debug("FCM not yet implemented: %s", notification.get("id"))
        return False


class EmailProvider(NotificationProvider):
    """Placeholder for email notification (not yet implemented)."""

    async def send(self, notification: dict[str, Any]) -> bool:
        logger.debug("EmailProvider not yet implemented: %s", notification.get("id"))
        return False


class SlackProvider(NotificationProvider):
    """Placeholder for Slack webhook (not yet implemented)."""

    async def send(self, notification: dict[str, Any]) -> bool:
        logger.debug("SlackProvider not yet implemented: %s", notification.get("id"))
        return False


class TeamsProvider(NotificationProvider):
    """Placeholder for Microsoft Teams webhook (not yet implemented)."""

    async def send(self, notification: dict[str, Any]) -> bool:
        logger.debug("TeamsProvider not yet implemented: %s", notification.get("id"))
        return False


# ── Event Dispatcher ───────────────────────────────────────────────

class EventDispatcher:
    """Coordinates audit logging and notification creation for domain events."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._providers: list[NotificationProvider] = [
            WebSocketProvider(),
            FirebaseCloudMessagingProvider(),
            EmailProvider(),
            SlackProvider(),
            TeamsProvider(),
        ]

    def register_provider(self, provider: NotificationProvider) -> None:
        self._providers.append(provider)

    async def dispatch_audit(
        self,
        table_name: str,
        record_id: str,
        action: str,
        performed_by: str | None = None,
        user_role: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=json.dumps(jsonable_encoder(old_values)) if old_values else None,
            new_values=json.dumps(jsonable_encoder(new_values)) if new_values else None,
            performed_by=performed_by,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            performed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(log)
        await self.db.flush()
        logger.info("Audit dispatched: %s on %s[%s] by %s", action, table_name, record_id, performed_by)
        return log

    async def dispatch_notification(
        self,
        title: str,
        message: str,
        category: str = NotificationCategory.SYSTEM,
        priority: str = NotificationPriority.MEDIUM,
        user_id: str | None = None,
        employee_id: str | None = None,
        recipient_role: str | None = None,
        reference_id: str | None = None,
        source: str | None = None,
        tenant_id: str | None = None,
        is_broadcast: bool = False,
    ) -> Notification:
        n = Notification(
            user_id=user_id,
            employee_id=employee_id,
            title=title,
            message=message,
            category=category,
            priority=priority,
            status=NotificationStatus.UNREAD,
            recipient_role=recipient_role,
            reference_id=reference_id,
            source=source,
            tenant_id=tenant_id,
            is_broadcast=is_broadcast,
        )
        self.db.add(n)
        await self.db.flush()
        await self.db.refresh(n)

        # Attempt delivery through registered providers
        n_dict = {c.name: getattr(n, c.name) for c in n.__table__.columns}
        for provider in self._providers:
            try:
                await provider.send(n_dict)
            except Exception as exc:
                logger.warning("Provider %s failed for notification %s: %s", type(provider).__name__, n.id, exc)

        logger.info("Notification dispatched: %s [%s]", title, n.id)
        return n

    async def dispatch_event(
        self,
        event_type: str,
        title: str,
        message: str | None = None,
        severity: str = "info",
        service_name: str | None = None,
        component: str | None = None,
        stack_trace: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
        hostname: str | None = None,
    ) -> Any:
        """Record a system-level event."""
        from app.models.system_activity import SystemActivity
        event = SystemActivity(
            event_type=event_type,
            severity=severity,
            title=title,
            message=message,
            service_name=service_name,
            component=component,
            stack_trace=stack_trace,
            metadata_json=json.dumps(jsonable_encoder(metadata)) if metadata else None,
            ip_address=ip_address,
            hostname=hostname,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        logger.info("System event dispatched: %s [%s]", event_type, event.id)
        return event
