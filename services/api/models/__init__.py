"""SQLAlchemy ORM models for Postgres metadata, profiles, and audit."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str] = mapped_column(Text, nullable=False, default="free")
    slack_webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    client_profiles: Mapped[list["ClientProfile"]] = relationship(back_populates="tenant")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="user")


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    naics_codes: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    states_of_operation: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    product_categories: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    supply_chain_jurisdictions: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="client_profiles")
    briefs: Mapped[list["Brief"]] = relationship(back_populates="client_profile")


class ChangeEvent(Base):
    __tablename__ = "change_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[str] = mapped_column(Text, nullable=False)
    clause_id: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(Text, nullable=False)
    old_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    briefs: Mapped[list["Brief"]] = relationship(back_populates="change_event")
    agent_traces: Mapped[list["AgentTrace"]] = relationship(back_populates="change_event")


class Brief(Base):
    __tablename__ = "briefs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False
    )
    change_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("change_events.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(Text, nullable=False)
    obligations: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    recommended_actions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    client_profile: Mapped["ClientProfile"] = relationship(back_populates="briefs")
    change_event: Mapped["ChangeEvent"] = relationship(back_populates="briefs")
    citations: Mapped[list["BriefCitation"]] = relationship(back_populates="brief")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="brief")
    agent_traces: Mapped[list["AgentTrace"]] = relationship(back_populates="brief")


class BriefCitation(Base):
    __tablename__ = "brief_citations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("briefs.id"), nullable=False
    )
    clause_id: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)

    brief: Mapped["Brief"] = relationship(back_populates="citations")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("briefs.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    rating: Mapped[str] = mapped_column(Text, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    hop_path: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    brief: Mapped["Brief"] = relationship(back_populates="feedback")
    user: Mapped["User"] = relationship(back_populates="feedback")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("briefs.id"), nullable=True
    )
    change_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("change_events.id"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    input_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    output_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    model_used: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    brief: Mapped["Brief | None"] = relationship(back_populates="agent_traces")
    change_event: Mapped["ChangeEvent"] = relationship(back_populates="agent_traces")
    llm_usage: Mapped[list["LLMUsage"]] = relationship(back_populates="trace")


class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_traces.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    trace: Mapped["AgentTrace"] = relationship(back_populates="llm_usage")


class RelevanceWeight(Base):
    __tablename__ = "relevance_weights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edge_type: Mapped[str] = mapped_column(Text, nullable=False)
    hop_depth: Mapped[int] = mapped_column(Integer, nullable=False)
    naics_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("briefs.id"), nullable=True
    )
    change_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("change_events.id"), nullable=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    alert_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite: Mapped[str] = mapped_column(Text, nullable=False)
    cases: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    details: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
