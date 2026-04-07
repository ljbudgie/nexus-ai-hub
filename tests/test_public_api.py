"""Tests for the top-level nexus_ai_hub public API."""

import nexus_ai_hub


class TestPublicAPI:
    """Ensure all key classes are importable from the top-level package."""

    def test_version(self) -> None:
        assert isinstance(nexus_ai_hub.__version__, str)

    def test_hermes_agent_exports(self) -> None:
        assert nexus_ai_hub.HermesAgent is not None
        assert nexus_ai_hub.AgentConfig is not None
        assert nexus_ai_hub.Conversation is not None
        assert nexus_ai_hub.Message is not None

    def test_mempalace_exports(self) -> None:
        assert nexus_ai_hub.MemPalace is not None
        assert nexus_ai_hub.Memory is not None

    def test_skills_exports(self) -> None:
        assert nexus_ai_hub.SkillRegistry is not None
        assert nexus_ai_hub.BaseSkill is not None
        assert nexus_ai_hub.SkillMetadata is not None

    def test_all_attribute(self) -> None:
        expected = {
            "AgentConfig",
            "BaseSkill",
            "Conversation",
            "HermesAgent",
            "Memory",
            "MemPalace",
            "Message",
            "SkillMetadata",
            "SkillRegistry",
            "__version__",
        }
        assert expected == set(nexus_ai_hub.__all__)
