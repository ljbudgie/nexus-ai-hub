"""Tests for the Skills registry module."""

import pytest

from nexus_ai_hub.skills.registry import BaseSkill, SkillMetadata, SkillRegistry


class EchoSkill(BaseSkill):
    """A simple test skill that echoes input."""

    metadata = SkillMetadata(name="echo", description="Echoes input back.", tags=["utility"])

    def execute(self, **kwargs: str) -> str:
        text = kwargs.get("text", "")
        return f"Echo: {text}"


class GreetSkill(BaseSkill):
    """A test skill that greets a user."""

    metadata = SkillMetadata(name="greet", description="Greet someone.")

    def execute(self, **kwargs: str) -> str:
        name = kwargs.get("name", "World")
        return f"Hello, {name}!"


class TestSkillRegistry:
    def test_register_and_run(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        result = registry.run("echo", text="hello")
        assert result == "Echo: hello"

    def test_register_duplicate_raises(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        with pytest.raises(ValueError, match="already registered"):
            registry.register(EchoSkill())

    def test_run_missing_skill_raises(self) -> None:
        registry = SkillRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.run("nonexistent")

    def test_get_skill(self) -> None:
        registry = SkillRegistry()
        registry.register(GreetSkill())
        skill = registry.get("greet")
        assert skill is not None
        assert skill.metadata.name == "greet"

    def test_get_missing_returns_none(self) -> None:
        registry = SkillRegistry()
        assert registry.get("missing") is None

    def test_list_skills(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        registry.register(GreetSkill())
        skills = registry.list_skills()
        names = [s.name for s in skills]
        assert "echo" in names
        assert "greet" in names

    def test_multiple_skills_run_independently(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        registry.register(GreetSkill())
        assert registry.run("echo", text="test") == "Echo: test"
        assert registry.run("greet", name="Alice") == "Hello, Alice!"

    def test_len(self) -> None:
        registry = SkillRegistry()
        assert len(registry) == 0
        registry.register(EchoSkill())
        assert len(registry) == 1
        registry.register(GreetSkill())
        assert len(registry) == 2

    def test_contains(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        assert "echo" in registry
        assert "missing" not in registry

    def test_repr(self) -> None:
        registry = SkillRegistry()
        assert "SkillRegistry" in repr(registry)
        assert "skills=0" in repr(registry)
        registry.register(EchoSkill())
        assert "skills=1" in repr(registry)
