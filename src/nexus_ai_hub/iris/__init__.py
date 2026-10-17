"""Iris — sovereign companion layer for sensory events (OpenHear).

Lightweight, local-first helper that surfaces OpenHear haptic events calmly
and in line with the Burgess Principle. No automated high-stakes decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nexus_ai_hub.core import NexusHub


@dataclass(frozen=True)
class IrisSurface:
    """A calm surface message for a sensory event."""

    event_type: str
    message: str
    haptic_ready: bool
    requires_human: bool


class IrisCompanion:
    """Local Iris companion that listens for OpenHear events."""

    def __init__(self, hub: NexusHub) -> None:
        self.hub = hub

    def on_haptic_event(
        self,
        event_type: str,
        facts: str,
        user_id: str = "local",
    ) -> IrisSurface:
        """Process a haptic event and return a calm surface message.

        Pure notifications (door knock, traffic, etc.) are treated as low-impact.
        Anything medical or high-stakes still goes through the full gate.
        """
        from nexus_ai_hub.core import BurgessContext

        is_pure_notification = event_type in {
            "door_knock",
            "doorbell",
            "traffic",
            "siren",
            "voice_nearby",
            "environmental_alert",
        }
        impact = "low" if is_pure_notification else "high"

        ctx = BurgessContext(
            domain="sensory",
            facts=facts,
            metadata={"user_id": user_id, "event_type": event_type, "impact_class": impact},
        )
        record = self.hub.review(f"iris_surface_{event_type}", ctx)
        allowed = self.hub.is_allowed(record)

        if allowed and is_pure_notification:
            message = f"{event_type.replace('_', ' ').title()} — haptic pattern ready."
            haptic_ready = True
            requires_human = False
        else:
            title = event_type.replace("_", " ").title()
            message = f"{title} requires human review before any action."
            haptic_ready = False
            requires_human = True

        return IrisSurface(
            event_type=event_type,
            message=message,
            haptic_ready=haptic_ready,
            requires_human=requires_human,
        )
