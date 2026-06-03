"""The Burgess Principle policy gate and tamper-evident accountability ledger.

The centrepiece of the ecosystem's promise is a single question::

    Was a human able to personally review the specific facts of this case?

This module makes that question *enforceable*. Every high-impact action is
classified ``SOVEREIGN`` (human review preserved) or ``NULL`` (a high-stakes
decision that would be automated, denied, obscured, or finalized without
adequate human review). NULL actions are blocked until a named human records an
approval.

Crucially, every decision and every human approval is appended to a
hash-chained ledger. Each record commits to the previous record's hash, so the
sequence behaves like a small, local, offline chain of accountability:

- You can prove *after the fact* that a specific decision received human review.
- You can prove that one did **not** — that an action was auto-finalized.
- Any tampering (deleting an inconvenient denial, back-dating an approval)
  breaks the chain and is detectable with a single :meth:`BurgessLedger.verify`
  call.

This inverts the usual power dynamic: normally the institution holds the audit
trail. Here the person holds it, locally, offline, and verifiably.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nexus_ai_hub.core import BurgessContext

__all__ = [
    "GENESIS_HASH",
    "BurgessBlockedError",
    "BurgessGate",
    "BurgessLedger",
    "Decision",
    "LedgerRecord",
]

#: The ``prev_hash`` of the first record in any chain (64 zeroes).
GENESIS_HASH = "0" * 64

#: Domains where an automated decision can materially affect a person's life.
#: Actions in these domains default to NULL until a human reviews them.
HIGH_IMPACT_DOMAINS: frozenset[str] = frozenset(
    {
        "legal",
        "medical",
        "medical_devices",
        "clinical",
        "institutional",
        "benefits",
        "welfare",
        "housing",
        "immigration",
        "employment",
        "education",
        "finance",
        "credit",
        "insurance",
        "denial",
        "appeal",
        "accommodation",
        "safety",
        "sensory_medical",
    }
)

#: Domains that are explicitly informational and carry no high-stakes side
#: effects. Only these (or an explicit low-impact declaration) classify as
#: SOVEREIGN without a human gate.
LOW_IMPACT_DOMAINS: frozenset[str] = frozenset(
    {
        "informational",
        "general",
        "lookup",
        "chat",
        "help",
        "documentation",
    }
)

#: Impact-class declarations (read from ``BurgessContext.metadata``) that are
#: treated as low-stakes.
_LOW_IMPACT_CLASSES: frozenset[str] = frozenset({"low", "informational", "none"})


class Decision(str, Enum):
    """The outcome of a Burgess Principle classification."""

    #: The workflow preserves human review, context, dignity, and agency.
    SOVEREIGN = "sovereign"
    #: The workflow would automate or finalize a high-stakes decision without
    #: adequate human review. Blocked until a human approves.
    NULL = "null"


class _RecordType(str, Enum):
    """The kind of event a ledger record captures."""

    CHECK = "burgess_check"
    APPROVAL = "human_approval"


class BurgessBlockedError(RuntimeError):
    """Raised when a NULL action is attempted without a recorded human review."""

    def __init__(self, record: LedgerRecord) -> None:
        self.record = record
        super().__init__(
            f"Action {record.action!r} (domain={record.domain!r}) was classified "
            f"NULL by the Burgess gate and is blocked pending human review. "
            f"Record a human approver via require_human(record_index={record.index})."
        )


@dataclass(frozen=True)
class LedgerRecord:
    """A single, immutable, hash-chained entry in the accountability ledger."""

    index: int
    timestamp: float
    record_type: str
    action: str
    domain: str
    decision: str
    rationale: str
    impact_class: str
    human_approver: str | None
    references: int | None
    prev_hash: str
    content_hash: str

    def payload(self) -> dict[str, Any]:
        """Return the canonical, hash-bearing fields (excludes ``content_hash``)."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "record_type": self.record_type,
            "action": self.action,
            "domain": self.domain,
            "decision": self.decision,
            "rationale": self.rationale,
            "impact_class": self.impact_class,
            "human_approver": self.human_approver,
            "references": self.references,
            "prev_hash": self.prev_hash,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict including ``content_hash``."""
        data = self.payload()
        data["content_hash"] = self.content_hash
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> LedgerRecord:
        """Reconstruct a record from a stored dict."""
        return cls(
            index=int(data["index"]),
            timestamp=float(data["timestamp"]),
            record_type=str(data["record_type"]),
            action=str(data["action"]),
            domain=str(data["domain"]),
            decision=str(data["decision"]),
            rationale=str(data["rationale"]),
            impact_class=str(data["impact_class"]),
            human_approver=(
                None if data["human_approver"] is None else str(data["human_approver"])
            ),
            references=(None if data["references"] is None else int(data["references"])),
            prev_hash=str(data["prev_hash"]),
            content_hash=str(data["content_hash"]),
        )


def _hash_payload(payload: Mapping[str, Any]) -> str:
    """Return the SHA-256 of a record's canonical payload."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class BurgessLedger:
    """An append-only, hash-chained ledger of Burgess decisions and approvals.

    When ``path`` is provided, records are persisted as newline-delimited JSON
    (JSONL): one record per line, human-readable, greppable, and trivially
    append-only. Existing files are loaded and verified on construction.

    Example::

        ledger = BurgessLedger(path="burgess.jsonl")
        gate = BurgessGate(ledger=ledger)
        record = gate.evaluate("send appeal letter", context)
        assert ledger.verify()
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path is not None else None
        self._records: list[LedgerRecord] = []
        if self._path is not None and self._path.exists():
            self._load()

    def _load(self) -> None:
        """Load records from the JSONL file at ``self._path``."""
        assert self._path is not None
        text = self._path.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            self._records.append(LedgerRecord.from_dict(json.loads(line)))

    @property
    def records(self) -> tuple[LedgerRecord, ...]:
        """Return all records as an immutable tuple."""
        return tuple(self._records)

    @property
    def last_hash(self) -> str:
        """Return the hash of the most recent record, or the genesis hash."""
        return self._records[-1].content_hash if self._records else GENESIS_HASH

    def append(
        self,
        *,
        record_type: _RecordType,
        action: str,
        domain: str,
        decision: Decision,
        rationale: str,
        impact_class: str,
        human_approver: str | None = None,
        references: int | None = None,
    ) -> LedgerRecord:
        """Append a new record, chaining it to the current tip of the ledger."""
        prev_hash = self.last_hash
        payload: dict[str, Any] = {
            "index": len(self._records),
            "timestamp": time.time(),
            "record_type": record_type.value,
            "action": action,
            "domain": domain,
            "decision": decision.value,
            "rationale": rationale,
            "impact_class": impact_class,
            "human_approver": human_approver,
            "references": references,
            "prev_hash": prev_hash,
        }
        record = LedgerRecord(content_hash=_hash_payload(payload), **payload)
        self._records.append(record)
        if self._path is not None:
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
        return record

    def verify(self) -> bool:
        """Return True if the chain is intact and untampered.

        Walks every record, confirming that each links to the previous record's
        hash and that each stored ``content_hash`` matches a fresh recomputation
        of its payload. Any mutation, deletion, reordering, or insertion breaks
        the chain and returns False.
        """
        prev = GENESIS_HASH
        for position, record in enumerate(self._records):
            if record.index != position:
                return False
            if record.prev_hash != prev:
                return False
            if record.content_hash != _hash_payload(record.payload()):
                return False
            prev = record.content_hash
        return True

    def get(self, index: int) -> LedgerRecord:
        """Return the record at ``index``."""
        return self._records[index]

    def __len__(self) -> int:
        """Return the number of records in the ledger."""
        return len(self._records)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"BurgessLedger(records={len(self._records)}, verified={self.verify()})"


#: A classifier maps an action and its context to a (decision, rationale) pair.
Classifier = Callable[[str, "BurgessContext"], "tuple[Decision, str]"]


def conservative_classifier(action: str, context: BurgessContext) -> tuple[Decision, str]:
    """Conservative, deny-by-default SOVEREIGN/NULL classifier.

    The default stance is suspicion: an action is SOVEREIGN only when it is
    *explicitly* low-impact (a known informational domain, or an
    ``impact_class`` declared low). Anything in a high-impact domain, anything
    declared high-impact, and anything *unrecognised* defaults to NULL — so a
    new or unclassified workflow fails closed, toward human review.

    Args:
        action: A short description of the action being attempted.
        context: The case-specific Burgess context. ``context.metadata`` may
            carry an ``"impact_class"`` hint of ``"low"`` or ``"high"``.

    Returns:
        A ``(decision, rationale)`` pair.
    """
    domain = context.domain.strip().lower()
    impact_class = context.metadata.get("impact_class", "").strip().lower()

    if impact_class == "high":
        return Decision.NULL, (
            f"Action {action!r} is declared high-impact; human review of the "
            "specific facts is required before it proceeds."
        )
    if impact_class in _LOW_IMPACT_CLASSES:
        return Decision.SOVEREIGN, (
            f"Action {action!r} is declared low-impact; no high-stakes decision "
            "is being finalized without review."
        )
    if domain in HIGH_IMPACT_DOMAINS:
        return Decision.NULL, (
            f"Domain {domain!r} can materially affect a person; {action!r} is "
            "blocked until a human reviews the specific facts of this case."
        )
    if domain in LOW_IMPACT_DOMAINS:
        return Decision.SOVEREIGN, (
            f"Domain {domain!r} is informational; {action!r} preserves human "
            "agency and needs no review gate."
        )
    return Decision.NULL, (
        f"Domain {domain!r} is unrecognised; failing closed toward human review "
        f"so {action!r} cannot finalize a high-stakes decision unseen."
    )


class BurgessGate:
    """Classifies actions and enforces human review, recording every step.

    The gate wraps any decision path that can affect a person. High-impact
    actions are classified NULL and must be released by a named human via
    :meth:`require_human` before :meth:`is_allowed` returns True.

    Example::

        gate = BurgessGate()
        record = gate.evaluate("issue benefits denial", context)
        if record.decision is Decision.NULL:
            gate.require_human(record, approver="caseworker:alex")
        assert gate.is_allowed(record)
        assert gate.ledger.verify()
    """

    def __init__(
        self,
        *,
        ledger: BurgessLedger | None = None,
        classifier: Classifier | None = None,
    ) -> None:
        self.ledger = ledger if ledger is not None else BurgessLedger()
        self._classify = classifier if classifier is not None else conservative_classifier

    def evaluate(self, action: str, context: BurgessContext) -> LedgerRecord:
        """Classify an action and append a check record to the ledger.

        Args:
            action: A short description of the action being attempted.
            context: The case-specific Burgess context.

        Returns:
            The appended ``burgess_check`` record. A NULL decision means the
            action is blocked until :meth:`require_human` records an approver.
        """
        decision, rationale = self._classify(action, context)
        return self.ledger.append(
            record_type=_RecordType.CHECK,
            action=action,
            domain=context.domain,
            decision=decision,
            rationale=rationale,
            impact_class=context.metadata.get("impact_class", ""),
        )

    def require_human(
        self,
        record: LedgerRecord | int,
        approver: str,
        note: str = "",
    ) -> LedgerRecord:
        """Record a human review that releases a NULL check.

        This never mutates the original check (that would break the chain).
        Instead it appends a new ``human_approval`` record that references the
        check by index, so the approval is itself part of the tamper-evident
        history.

        Args:
            record: The check record (or its index) being approved.
            approver: A stable identifier for the human who reviewed the facts.
            note: Optional rationale for the approval.

        Returns:
            The appended ``human_approval`` record.

        Raises:
            ValueError: If the referenced record is not a Burgess check.
        """
        check = self._resolve(record)
        if check.record_type != _RecordType.CHECK.value:
            raise ValueError(
                f"Record {check.index} is a {check.record_type!r}, not a Burgess "
                "check; only checks can be approved."
            )
        return self.ledger.append(
            record_type=_RecordType.APPROVAL,
            action=check.action,
            domain=check.domain,
            decision=Decision.SOVEREIGN,
            rationale=note or f"Human {approver!r} reviewed the specific facts.",
            impact_class=check.impact_class,
            human_approver=approver,
            references=check.index,
        )

    def is_allowed(self, record: LedgerRecord | int) -> bool:
        """Return True if a check is SOVEREIGN or has a recorded human approval.

        Args:
            record: The check record (or its index) to evaluate.

        Returns:
            True if the action may proceed; False if it remains blocked.
        """
        check = self._resolve(record)
        if check.decision == Decision.SOVEREIGN.value:
            return True
        return any(
            entry.record_type == _RecordType.APPROVAL.value
            and entry.references == check.index
            for entry in self.ledger.records
        )

    def _resolve(self, record: LedgerRecord | int) -> LedgerRecord:
        """Return the ledger record for a record or its index."""
        if isinstance(record, LedgerRecord):
            return record
        return self.ledger.get(record)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"BurgessGate(ledger={self.ledger!r})"
