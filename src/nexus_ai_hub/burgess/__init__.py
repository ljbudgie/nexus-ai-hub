"""Executable Burgess Principle enforcement.

This package turns the Burgess Principle from doctrine into a running,
inspectable policy layer:

- A conservative, deny-by-default SOVEREIGN/NULL classifier.
- A ``BurgessGate`` that blocks high-impact actions until a human review is
  recorded.
- A tamper-evident, hash-chained ``BurgessLedger`` so anyone can later *prove*
  whether a human-review gate was honoured for a given decision.

The guiding rule, made enforceable:

    If a system affects a human life, the human must remain visible,
    reviewable, and sovereign.
"""

from nexus_ai_hub.burgess.gate import (
    GENESIS_HASH,
    BurgessBlockedError,
    BurgessGate,
    BurgessLedger,
    Decision,
    LedgerRecord,
)

__all__ = [
    "GENESIS_HASH",
    "BurgessBlockedError",
    "BurgessGate",
    "BurgessLedger",
    "Decision",
    "LedgerRecord",
]
