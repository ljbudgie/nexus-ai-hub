"""Tests for the top-level nexus_ai_hub public API."""

import nexus_ai_hub
from nexus_ai_hub import BurgessContext, NexusHub
from nexus_ai_hub.hermes_agent import AgentConfig, Conversation, HermesAgent, Message
from nexus_ai_hub.mempalace import Memory, MemPalace
from nexus_ai_hub.skills import BaseSkill, SkillMetadata, SkillRegistry


class TestPublicAPI:
    """Ensure all key classes are importable from the top-level package."""

    def test_version(self) -> None:
        assert isinstance(nexus_ai_hub.__version__, str)

    def test_version_format(self) -> None:
        parts = nexus_ai_hub.__version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

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

    def test_hub_exports(self) -> None:
        assert nexus_ai_hub.NexusHub is not None
        assert nexus_ai_hub.BurgessContext is not None

    def test_all_attribute(self) -> None:
        expected = {
            "AgentConfig",
            "BaseSkill",
            "BurgessContext",
            "BurgessIntegration",
            "Conversation",
            "HermesAgent",
            "HapticProfile",
            "Memory",
            "MemPalace",
            "Message",
            "MirrorIntegration",
            "MirrorRights",
            "NexusHub",
            "OpenHearIntegration",
            "SkillMetadata",
            "SkillRegistry",
            "__version__",
        }
        assert expected == set(nexus_ai_hub.__all__)


class TestSubPackageImports:
    """Ensure classes are importable from their sub-packages."""

    def test_hermes_agent_subpackage(self) -> None:
        assert HermesAgent is nexus_ai_hub.HermesAgent
        assert AgentConfig is nexus_ai_hub.AgentConfig
        assert Conversation is nexus_ai_hub.Conversation
        assert Message is nexus_ai_hub.Message

    def test_mempalace_subpackage(self) -> None:
        assert MemPalace is nexus_ai_hub.MemPalace
        assert Memory is nexus_ai_hub.Memory

    def test_skills_subpackage(self) -> None:
        assert SkillRegistry is nexus_ai_hub.SkillRegistry
        assert BaseSkill is nexus_ai_hub.BaseSkill
        assert SkillMetadata is nexus_ai_hub.SkillMetadata

    def test_hub_top_level_imports(self) -> None:
        assert NexusHub is nexus_ai_hub.NexusHub
        assert BurgessContext is nexus_ai_hub.BurgessContext

    def test_hermes_agent_subpackage_all(self) -> None:
        from nexus_ai_hub.hermes_agent import __all__ as ha_all

        assert set(ha_all) == {"AgentConfig", "Conversation", "HermesAgent", "Message"}

    def test_mempalace_subpackage_all(self) -> None:
        from nexus_ai_hub.mempalace import __all__ as mp_all

        assert set(mp_all) == {"Memory", "MemPalace"}

    def test_skills_subpackage_all(self) -> None:
        from nexus_ai_hub.skills import __all__ as sk_all

        assert set(sk_all) == {"BaseSkill", "SkillMetadata", "SkillRegistry"}
