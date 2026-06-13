"""Tests for CRITICAL brief notifications."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.api.models import Brief, ChangeEvent, ClientProfile, Tenant
from services.api.services.notifications import notify_critical_brief


@pytest.mark.asyncio
async def test_notify_critical_brief_sends_slack() -> None:
    tenant_id = uuid.uuid4()
    brief_id = uuid.uuid4()
    change_id = uuid.uuid4()
    client_id = uuid.uuid4()

    brief = Brief(
        id=brief_id,
        client_id=client_id,
        change_event_id=change_id,
        title="Critical labeling change",
        change_summary="New allergen rule",
        severity="CRITICAL",
        obligations=[],
        recommended_actions=[],
        confidence=Decimal("0.95"),
        status="COMPLETE",
        disclaimer="Not legal advice",
    )
    change = ChangeEvent(
        id=change_id,
        document_id="ecfr-21-101",
        clause_id="ecfr:21:101:101.1",
        change_type="MODIFIED",
        severity="CRITICAL",
        source="ecfr",
    )
    profile = ClientProfile(
        id=client_id,
        tenant_id=tenant_id,
        name="Acme Foods",
        naics_codes=["311412"],
        states_of_operation=["CA"],
        product_categories=["snacks"],
        supply_chain_jurisdictions=["US"],
    )
    tenant = Tenant(id=tenant_id, name="Acme Tenant", plan="pro")

    db = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=execute_result)

    with (
        patch("services.api.services.notifications.get_settings") as settings_mock,
        patch(
            "services.api.services.notifications._already_sent",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch(
            "services.api.services.notifications._send_slack",
            new_callable=AsyncMock,
        ) as slack_mock,
    ):
        settings = settings_mock.return_value
        settings.alert_channel_list = ["slack"]
        settings.slack_webhook_url = "https://hooks.slack.com/test"
        settings.app_base_url = "http://localhost:3000"
        settings.ses_from_email = ""

        await notify_critical_brief(
            db,
            brief=brief,
            change_event=change,
            client_profile=profile,
            tenant=tenant,
        )

    slack_mock.assert_awaited_once()
    db.flush.assert_awaited()
