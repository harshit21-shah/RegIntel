"""Slack and email notifications for CRITICAL regulatory briefs."""

from __future__ import annotations

import logging
import uuid
from typing import Literal

import boto3
import httpx
from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.config import Settings, get_settings
from services.api.models import AlertDelivery, Brief, ChangeEvent, ClientProfile, Tenant, User

logger = logging.getLogger(__name__)

AlertType = Literal["critical_brief", "critical_review"]


async def _already_sent(
    db: AsyncSession,
    *,
    brief_id: uuid.UUID | None,
    change_event_id: uuid.UUID | None,
    channel: str,
    alert_type: AlertType,
) -> bool:
    result = await db.execute(
        select(AlertDelivery).where(
            AlertDelivery.brief_id == brief_id,
            AlertDelivery.change_event_id == change_event_id,
            AlertDelivery.channel == channel,
            AlertDelivery.alert_type == alert_type,
        )
    )
    return result.scalar_one_or_none() is not None


async def _record_delivery(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    brief_id: uuid.UUID | None,
    change_event_id: uuid.UUID | None,
    channel: str,
    alert_type: AlertType,
    status: str,
    error_message: str | None = None,
) -> None:
    db.add(
        AlertDelivery(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            brief_id=brief_id,
            change_event_id=change_event_id,
            channel=channel,
            alert_type=alert_type,
            status=status,
            error_message=error_message,
        )
    )
    await db.flush()


def _brief_url(brief_id: uuid.UUID, settings: Settings) -> str:
    return f"{settings.app_base_url.rstrip('/')}/briefs/{brief_id}"


async def _send_slack(
    webhook_url: str,
    *,
    text: str,
    blocks: list[dict[str, object]] | None = None,
) -> None:
    payload: dict[str, object] = {"text": text}
    if blocks:
        payload["blocks"] = blocks
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()


async def _send_email(
    *,
    recipients: list[str],
    subject: str,
    body: str,
    settings: Settings,
) -> None:
    if not settings.ses_from_email or not recipients:
        return
    client = boto3.client("ses", region_name=settings.aws_region)
    try:
        client.send_email(
            Source=settings.ses_from_email,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
    except ClientError:
        logger.exception("SES send failed")
        raise


async def notify_critical_brief(
    db: AsyncSession,
    *,
    brief: Brief,
    change_event: ChangeEvent,
    client_profile: ClientProfile,
    tenant: Tenant,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    if brief.severity != "CRITICAL" or brief.status != "COMPLETE":
        return

    alert_type: AlertType = "critical_brief"
    title = f"CRITICAL: {brief.title}"
    summary = (
        f"Client: {client_profile.name}\n"
        f"Severity: {brief.severity}\n"
        f"Summary: {brief.change_summary[:500]}\n"
        f"View: {_brief_url(brief.id, settings)}"
    )

    user_rows = await db.execute(
        select(User.email).where(
            User.tenant_id == tenant.id,
            User.role.in_(("admin", "consultant")),
        )
    )
    recipients = [str(email) for email in user_rows.scalars().all() if email]

    slack_urls = [url for url in (settings.slack_webhook_url, tenant.slack_webhook_url) if url]

    for channel in settings.alert_channel_list:
        if channel == "slack":
            for webhook in dict.fromkeys(slack_urls):
                if await _already_sent(
                    db,
                    brief_id=brief.id,
                    change_event_id=change_event.id,
                    channel="slack",
                    alert_type=alert_type,
                ):
                    continue
                try:
                    await _send_slack(
                        webhook,
                        text=title,
                        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": summary}}],
                    )
                    await _record_delivery(
                        db,
                        tenant_id=tenant.id,
                        brief_id=brief.id,
                        change_event_id=change_event.id,
                        channel="slack",
                        alert_type=alert_type,
                        status="SENT",
                    )
                except Exception as exc:
                    await _record_delivery(
                        db,
                        tenant_id=tenant.id,
                        brief_id=brief.id,
                        change_event_id=change_event.id,
                        channel="slack",
                        alert_type=alert_type,
                        status="FAILED",
                        error_message=str(exc),
                    )
        elif channel == "email":
            if await _already_sent(
                db,
                brief_id=brief.id,
                change_event_id=change_event.id,
                channel="email",
                alert_type=alert_type,
            ):
                continue
            try:
                await _send_email(
                    recipients=recipients,
                    subject=title,
                    body=summary,
                    settings=settings,
                )
                await _record_delivery(
                    db,
                    tenant_id=tenant.id,
                    brief_id=brief.id,
                    change_event_id=change_event.id,
                    channel="email",
                    alert_type=alert_type,
                    status="SENT",
                )
            except Exception as exc:
                await _record_delivery(
                    db,
                    tenant_id=tenant.id,
                    brief_id=brief.id,
                    change_event_id=change_event.id,
                    channel="email",
                    alert_type=alert_type,
                    status="FAILED",
                    error_message=str(exc),
                )


async def notify_critical_review_required(
    db: AsyncSession,
    *,
    change_event: ChangeEvent,
    tenant_id: uuid.UUID,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    if change_event.severity != "CRITICAL":
        return

    alert_type: AlertType = "critical_review"
    summary = (
        f"A CRITICAL regulatory change requires human review.\n"
        f"Clause: {change_event.clause_id}\n"
        f"Document: {change_event.document_id}\n"
        f"Verification did not pass — no brief was generated."
    )
    tenant_row = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_row.scalar_one_or_none()
    if tenant is None:
        return

    slack_urls = [url for url in (settings.slack_webhook_url, tenant.slack_webhook_url) if url]
    for webhook in dict.fromkeys(slack_urls):
        if await _already_sent(
            db,
            brief_id=None,
            change_event_id=change_event.id,
            channel="slack",
            alert_type=alert_type,
        ):
            continue
        try:
            await _send_slack(
                webhook,
                text="CRITICAL change needs review",
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": summary}}],
            )
            await _record_delivery(
                db,
                tenant_id=tenant.id,
                brief_id=None,
                change_event_id=change_event.id,
                channel="slack",
                alert_type=alert_type,
                status="SENT",
            )
        except Exception as exc:
            await _record_delivery(
                db,
                tenant_id=tenant.id,
                brief_id=None,
                change_event_id=change_event.id,
                channel="slack",
                alert_type=alert_type,
                status="FAILED",
                error_message=str(exc),
            )
