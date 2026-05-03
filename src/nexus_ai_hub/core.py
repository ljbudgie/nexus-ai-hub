"""Unified Nexus AI Hub orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass, field

from nexus_ai_hub.hermes_agent.agent import HermesAgent
from nexus_ai_hub.mempalace.palace import MemPalace

__all__ = [
    "BurgessContext",
    "HapticProfile",
    "MirrorRights",
    "NexusHub",
    "OpenHearIntegration",
    "BurgessIntegration",
    "MirrorIntegration",
]


@dataclass
class BurgessContext:
    """Case-specific context for Burgess Principle review."""

    domain: str
    facts: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MirrorRights:
    """A lightweight rights summary for a Mirror case context."""

    domain: str
    summary: str
    rights: tuple[str, ...]
    human_review_required: bool = True


@dataclass(frozen=True)
class HapticProfile:
    """A lightweight OpenHear haptic profile."""

    user_id: str
    pattern_id: str
    channels: tuple[str, ...] = ("left_wrist_outer",)
    rhythm: str = "double_pulse"
    duration_ms: int = 450
    intensity: float = 0.45
    semantic_label: str = "accessibility_alert"


class MirrorIntegration:
    """Mirror adapter for rights mapping and institutional accountability workflows."""

    def get_rights(self, context: BurgessContext) -> MirrorRights:
        """Return rights and review signals for a case context.

        Args:
            context: Case-specific Burgess context.

        Returns:
            A lightweight rights summary for the supplied domain and facts.
        """
        domain_label = context.domain.replace("_", " ")
        rights = (
            "Human review of the specific facts",
            "Clear reasons for any automated or institutional decision",
            "Accessible challenge or appeal route",
        )
        return MirrorRights(
            domain=context.domain,
            summary=f"Mirror rights map for {domain_label}: {context.facts}",
            rights=rights,
        )


class BurgessIntegration:
    """Burgess Principle adapter for generating human-review prompts."""

    def generate_question(self, context: BurgessContext) -> str:
        """Generate the Burgess Principle question for a case context.

        Args:
            context: Case-specific Burgess context.

        Returns:
            The human-review question grounded in the supplied context.
        """
        domain_label = context.domain.replace("_", " ")
        return (
            "Was a human able to personally review the specific facts of this "
            f"{domain_label} case before the decision was made?"
        )


class OpenHearIntegration:
    """OpenHear adapter for sensory and haptic profile workflows."""

    def get_haptic_profile(self, user_id: str) -> HapticProfile:
        """Return a default local haptic profile for a user.

        Args:
            user_id: The local user identifier.

        Returns:
            A lightweight haptic profile suitable for storage in MemPalace.
        """
        return HapticProfile(user_id=user_id, pattern_id=f"haptic_profile_{user_id}")


class NexusHub:
    """Unified entry point for the Nexus AI Hub ecosystem."""

    def __init__(
        self,
        *,
        agent: HermesAgent | None = None,
        mempalace: MemPalace | None = None,
        mirror: MirrorIntegration | None = None,
        burgess: BurgessIntegration | None = None,
        openhear: OpenHearIntegration | None = None,
    ) -> None:
        self.agent = agent or HermesAgent()
        self.mempalace = mempalace or MemPalace()
        self.mirror = mirror or MirrorIntegration()
        self.burgess = burgess or BurgessIntegration()
        self.openhear = openhear or OpenHearIntegration()

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return (
            "NexusHub("
            f"agent={self.agent!r}, "
            f"mempalace={self.mempalace!r}, "
            "mirror=MirrorIntegration(), "
            "burgess=BurgessIntegration(), "
            "openhear=OpenHearIntegration()"
            ")"
        )
