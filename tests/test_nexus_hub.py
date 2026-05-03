"""Tests for the unified NexusHub entry point."""

import nexus_ai_hub
from nexus_ai_hub import BurgessContext, NexusHub
from nexus_ai_hub.core import HapticProfile, MirrorRights


class TestNexusHub:
    """Tests for ecosystem-level hub orchestration."""

    def test_problem_statement_usage(self) -> None:
        hub = NexusHub()
        context = BurgessContext(
            domain="medical_devices",
            facts="User received automated denial for hearing aid funding.",
        )

        rights = hub.mirror.get_rights(context)
        question = hub.burgess.generate_question(context)
        haptic_profile = hub.openhear.get_haptic_profile(user_id="123")
        memory = hub.mempalace.store_sensory("haptic_pattern_42", haptic_profile)
        response = hub.agent.chat(
            "Help me challenge this decision and adjust my hearing profile",
            context=context,
        )

        assert isinstance(rights, MirrorRights)
        assert rights.domain == "medical_devices"
        assert rights.human_review_required is True
        assert "Human review" in rights.rights[0]
        assert "personally review" in question
        assert isinstance(haptic_profile, HapticProfile)
        assert haptic_profile.user_id == "123"
        assert memory.key == "haptic_pattern_42"
        assert "sensory" in memory.tags
        assert "123" in memory.content
        assert "medical_devices" in response

    def test_hub_components_are_independent_per_instance(self) -> None:
        hub1 = NexusHub()
        hub2 = NexusHub()

        hub1.mempalace.store("case", "one")

        assert hub1.mempalace.recall("case") is not None
        assert hub2.mempalace.recall("case") is None
        assert hub1.agent is not hub2.agent

    def test_top_level_exports(self) -> None:
        assert nexus_ai_hub.NexusHub is NexusHub
        assert nexus_ai_hub.BurgessContext is BurgessContext
        assert "NexusHub" in nexus_ai_hub.__all__
        assert "BurgessContext" in nexus_ai_hub.__all__
