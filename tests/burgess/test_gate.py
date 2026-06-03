"""Tests for the executable Burgess Principle gate and accountability ledger."""

import dataclasses
import json

import pytest

from nexus_ai_hub import (
    BurgessBlockedError,
    BurgessContext,
    BurgessGate,
    BurgessLedger,
    Decision,
    NexusHub,
    SkillMetadata,
    SkillRegistry,
)
from nexus_ai_hub.burgess.gate import GENESIS_HASH
from nexus_ai_hub.skills.registry import BaseSkill


def high_impact_ctx() -> BurgessContext:
    return BurgessContext(
        domain="medical_devices",
        facts="Automated denial of hearing-aid funding.",
    )


def low_impact_ctx() -> BurgessContext:
    return BurgessContext(domain="informational", facts="Explain the appeals process.")


class TestClassifier:
    """The conservative, deny-by-default SOVEREIGN/NULL classifier."""

    def test_high_impact_domain_is_null(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        assert record.decision == Decision.NULL.value

    def test_informational_domain_is_sovereign(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("explain process", low_impact_ctx())
        assert record.decision == Decision.SOVEREIGN.value

    def test_unknown_domain_fails_closed_to_null(self) -> None:
        gate = BurgessGate()
        ctx = BurgessContext(domain="some_new_unmapped_domain", facts="?")
        record = gate.evaluate("do thing", ctx)
        assert record.decision == Decision.NULL.value

    def test_explicit_low_impact_class_overrides_unknown_domain(self) -> None:
        gate = BurgessGate()
        ctx = BurgessContext(
            domain="some_new_unmapped_domain",
            facts="?",
            metadata={"impact_class": "low"},
        )
        record = gate.evaluate("do thing", ctx)
        assert record.decision == Decision.SOVEREIGN.value

    def test_explicit_high_impact_class_overrides_safe_domain(self) -> None:
        gate = BurgessGate()
        ctx = BurgessContext(
            domain="informational",
            facts="?",
            metadata={"impact_class": "high"},
        )
        record = gate.evaluate("do thing", ctx)
        assert record.decision == Decision.NULL.value


class TestHumanReviewGate:
    """NULL actions are blocked until a named human reviews them."""

    def test_sovereign_is_allowed_without_approval(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("explain process", low_impact_ctx())
        assert gate.is_allowed(record) is True

    def test_null_is_blocked_until_approved(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        assert gate.is_allowed(record) is False

        gate.require_human(record, approver="caseworker:alex")
        assert gate.is_allowed(record) is True

    def test_approval_records_the_named_human(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        approval = gate.require_human(record, approver="caseworker:alex", note="Reviewed.")
        assert approval.human_approver == "caseworker:alex"
        assert approval.references == record.index
        assert approval.decision == Decision.SOVEREIGN.value

    def test_approval_does_not_mutate_the_original_check(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        gate.require_human(record, approver="caseworker:alex")
        # The original check is still NULL; allowance comes from the appended
        # approval, not from rewriting history.
        assert gate.ledger.get(record.index).decision == Decision.NULL.value

    def test_cannot_approve_an_approval(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        approval = gate.require_human(record, approver="caseworker:alex")
        with pytest.raises(ValueError, match="not a Burgess"):
            gate.require_human(approval, approver="someone_else")

    def test_resolve_by_index(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("issue denial", high_impact_ctx())
        gate.require_human(record.index, approver="caseworker:alex")
        assert gate.is_allowed(record.index) is True


class TestHashChain:
    """The ledger behaves as a tamper-evident hash chain."""

    def test_empty_ledger_verifies(self) -> None:
        assert BurgessLedger().verify() is True

    def test_first_record_links_to_genesis(self) -> None:
        gate = BurgessGate()
        record = gate.evaluate("explain process", low_impact_ctx())
        assert record.prev_hash == GENESIS_HASH
        assert record.index == 0

    def test_each_record_links_to_the_previous(self) -> None:
        gate = BurgessGate()
        first = gate.evaluate("explain process", low_impact_ctx())
        second = gate.evaluate("issue denial", high_impact_ctx())
        assert second.prev_hash == first.content_hash
        assert gate.ledger.verify() is True

    def test_tampering_with_content_breaks_the_chain(self) -> None:
        gate = BurgessGate()
        gate.evaluate("issue denial", high_impact_ctx())
        gate.evaluate("explain process", low_impact_ctx())
        assert gate.ledger.verify() is True

        # Flip a NULL denial into a SOVEREIGN record without recomputing its
        # hash — exactly the kind of quiet rewrite the ledger must catch.
        tampered = dataclasses.replace(
            gate.ledger.records[0], decision=Decision.SOVEREIGN.value
        )
        gate.ledger._records[0] = tampered  # type: ignore[attr-defined]
        assert gate.ledger.verify() is False

    def test_deleting_a_record_breaks_the_chain(self) -> None:
        gate = BurgessGate()
        gate.evaluate("issue denial", high_impact_ctx())
        gate.evaluate("explain process", low_impact_ctx())
        del gate.ledger._records[0]  # type: ignore[attr-defined]
        assert gate.ledger.verify() is False


class TestPersistence:
    """The JSONL ledger persists across process boundaries."""

    def test_round_trip_reload_verifies(self, tmp_path) -> None:
        path = tmp_path / "burgess.jsonl"
        gate = BurgessGate(ledger=BurgessLedger(path=path))
        record = gate.evaluate("issue denial", high_impact_ctx())
        gate.require_human(record, approver="caseworker:alex")

        reloaded = BurgessLedger(path=path)
        assert len(reloaded) == 2
        assert reloaded.verify() is True
        assert reloaded.last_hash == gate.ledger.last_hash

    def test_each_record_is_one_jsonl_line(self, tmp_path) -> None:
        path = tmp_path / "burgess.jsonl"
        gate = BurgessGate(ledger=BurgessLedger(path=path))
        gate.evaluate("explain process", low_impact_ctx())
        gate.evaluate("issue denial", high_impact_ctx())
        lines = [line for line in path.read_text().splitlines() if line.strip()]
        assert len(lines) == 2
        assert all("content_hash" in json.loads(line) for line in lines)

    def test_appending_continues_an_existing_chain(self, tmp_path) -> None:
        path = tmp_path / "burgess.jsonl"
        BurgessGate(ledger=BurgessLedger(path=path)).evaluate(
            "explain process", low_impact_ctx()
        )

        resumed = BurgessGate(ledger=BurgessLedger(path=path))
        second = resumed.evaluate("issue denial", high_impact_ctx())
        assert second.index == 1
        assert resumed.ledger.verify() is True

    def test_external_file_tampering_is_detected_on_reload(self, tmp_path) -> None:
        path = tmp_path / "burgess.jsonl"
        gate = BurgessGate(ledger=BurgessLedger(path=path))
        gate.evaluate("issue denial", high_impact_ctx())

        raw = json.loads(path.read_text().splitlines()[0])
        raw["decision"] = Decision.SOVEREIGN.value  # rewrite history on disk
        path.write_text(json.dumps(raw, sort_keys=True) + "\n")

        assert BurgessLedger(path=path).verify() is False


class _DenialSkill(BaseSkill):
    metadata = SkillMetadata(
        name="issue_denial",
        description="Issue an institutional denial.",
        domain="institutional",
        impact_class="high",
    )

    def execute(self, **kwargs: str) -> str:
        return "denial issued"


class _ExplainSkill(BaseSkill):
    metadata = SkillMetadata(
        name="explain",
        description="Explain a process.",
        domain="informational",
    )

    def execute(self, **kwargs: str) -> str:
        return "explained"


class TestSkillRegistryEnforcement:
    """A gated registry blocks high-impact skills until reviewed."""

    def test_registry_without_gate_runs_freely(self) -> None:
        registry = SkillRegistry()
        registry.register(_DenialSkill())
        assert registry.run("issue_denial") == "denial issued"

    def test_gated_high_impact_skill_is_blocked(self) -> None:
        gate = BurgessGate()
        registry = SkillRegistry(gate=gate)
        registry.register(_DenialSkill())
        with pytest.raises(BurgessBlockedError):
            registry.run("issue_denial")

    def test_gated_high_impact_skill_runs_with_approver(self) -> None:
        gate = BurgessGate()
        registry = SkillRegistry(gate=gate)
        registry.register(_DenialSkill())
        assert registry.run("issue_denial", approver="caseworker:alex") == "denial issued"
        assert gate.ledger.verify() is True

    def test_gated_informational_skill_runs_without_approver(self) -> None:
        gate = BurgessGate()
        registry = SkillRegistry(gate=gate)
        registry.register(_ExplainSkill())
        assert registry.run("explain") == "explained"


class TestNexusHubIntegration:
    """The hub exposes review/approve helpers over a shared gate."""

    def test_hub_review_and_approve(self) -> None:
        hub = NexusHub()
        record = hub.review("issue denial", high_impact_ctx())
        assert hub.is_allowed(record) is False
        hub.approve(record, approver="caseworker:alex")
        assert hub.is_allowed(record) is True
        assert hub.gate.ledger.verify() is True

    def test_each_hub_has_an_independent_ledger(self) -> None:
        hub1 = NexusHub()
        hub2 = NexusHub()
        hub1.review("issue denial", high_impact_ctx())
        assert len(hub1.gate.ledger) == 1
        assert len(hub2.gate.ledger) == 0
