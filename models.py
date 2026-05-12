from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TransactionLogEntry(BaseModel):
    """Pojedynczy wpis w transaction_log (log transakcji)."""

    timestamp: str
    tcode: str
    description: str


class ChangeLogEntry(BaseModel):
    """Pojedynczy wpis w change_log (zmiana danych w tabeli)."""

    timestamp: str
    table: str
    key: str
    field: str
    old_value: str
    new_value: str


class SystemLogEntry(BaseModel):
    """Pojedynczy wpis w system_log (komunikat systemowy)."""

    timestamp: str
    message: str
    type: str


class OsCommandLogEntry(BaseModel):
    """Pojedynczy wpis w os_command_log (polecenie OS)."""

    timestamp: str
    command: str
    parameters: str
    executed_by: str


class SessionLog(BaseModel):
    """Sesja SAP Firefighter — wejście do analizy zgodności."""

    session_id: str
    firefighter_id: str
    firefighter_user: str
    controller: str
    system: str
    client: str
    start_time: str
    end_time: str
    reason_code: str
    ticket_reference: str
    ticket_requester: Optional[str] = None
    alert_source: Optional[str] = None
    transaction_log: List[TransactionLogEntry] = Field(default_factory=list)
    change_log: List[ChangeLogEntry] = Field(default_factory=list)
    system_log: List[SystemLogEntry] = Field(default_factory=list)
    os_command_log: List[OsCommandLogEntry] = Field(default_factory=list)


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Finding(BaseModel):
    """Pojedyncze ustalenie / naruszenie reguły w wyniku przeglądu."""

    rule_id: str
    severity: Severity
    location: str
    description: str
    evidence: str


class SuggestedCorrection(BaseModel):
    """Sugerowana korekta dla strażaka."""

    message_to_firefighter: str
    suggested_reason_rewrite: Optional[str] = None


class Verdict(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    NEEDS_CORRECTION = "NEEDS_CORRECTION"


class ReviewResult(BaseModel):
    """Wynik przeglądu sesji — format zgodny z labels.jsonl / predykcjami dla eval.py."""

    session_id: str
    verdict: Verdict
    findings: List[Finding] = Field(default_factory=list)
    suggested_correction: Optional[SuggestedCorrection] = None
