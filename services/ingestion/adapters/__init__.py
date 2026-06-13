"""Regulatory source adapters."""

from services.ingestion.adapters.base import SourceAdapter
from services.ingestion.adapters.ecfr import EcfrAdapter
from services.ingestion.adapters.federal_register import FederalRegisterAdapter

__all__ = ["EcfrAdapter", "FederalRegisterAdapter", "SourceAdapter"]
