"""Tests for the Skills registry module."""

import pytest

from nexus_ai_hub.skills.registry import BaseSkill, SkillMetadata, SkillRegistry


class EchoSkill(BaseSkill):
    """A simple test skill that echoes input."""

    metadata = SkillMetadata(name="echo", description="Echoes input back.", tags=["utility"])

    def execute(self, **kwargs: str) -> str:
        text = kwargs.get("text", "")
        return f"Echo: {text}"


class AlternateEchoSkill(BaseSkill):
    """A skill with a duplicate name used to verify duplicate registration behavior."""

    metadata = SkillMetadata(name="echo", description="Alternate echo.")

    def execute(self, **kwargs: str) -> str:
        return "Alternate"


class GreetSkill(BaseSkill):
    """A test skill that greets a user."""

    metadata = SkillMetadata(name="greet", description="Greet someone.")

    def execute(self, **kwargs: str) -> str:
        name = kwargs.get("name", "World")
        return f"Hello, {name}!"


class UpperSkill(BaseSkill):
    """A test skill that uppercases text."""

    metadata = SkillMetadata(
        name="upper",
        description="Uppercase text.",
        version="1.0.0",
        tags=["text", "transform"],
    )

    def execute(self, **kwargs: str) -> str:
        return kwargs.get("text", "").upper()


class PairSkill(BaseSkill):
    """A test skill that combines two arguments."""

    metadata = SkillMetadata(name="pair", description="Join two values.")

    def execute(self, **kwargs: str) -> str:
        return f"{kwargs.get('left', '')}:{kwargs.get('right', '')}"


class TestSkillMetadata:
    """Tests for SkillMetadata defaults and custom values."""

    def test_defaults(self) -> None:
        meta = SkillMetadata(name="test", description="A test skill.")
        assert meta.name == "test"
        assert meta.description == "A test skill."
        assert meta.version == "0.1.0"
        assert meta.tags == []

    def test_custom_values(self) -> None:
        meta = SkillMetadata(
            name="advanced",
            description="An advanced skill.",
            version="2.0.0",
            tags=["ai", "ml"],
        )
        assert meta.name == "advanced"
        assert meta.version == "2.0.0"
        assert meta.tags == ["ai", "ml"]

    def test_tags_default_factory_isolation(self) -> None:
        """Each SkillMetadata instance should get its own tags list."""
        meta1 = SkillMetadata(name="a", description="a")
        meta2 = SkillMetadata(name="b", description="b")
        meta1.tags.append("x")
        assert "x" not in meta2.tags


class TestBaseSkill:
    def test_cannot_instantiate_directly(self) -> None:
        """BaseSkill is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseSkill()  # type: ignore[abstract]

    def test_concrete_skill_has_metadata(self) -> None:
        skill = EchoSkill()
        assert skill.metadata.name == "echo"
        assert skill.metadata.description == "Echoes input back."

    def test_concrete_skill_execute(self) -> None:
        skill = GreetSkill()
        result = skill.execute(name="Alice")
        assert result == "Hello, Alice!"

    def test_skill_execute_default_kwargs(self) -> None:
        skill = GreetSkill()
        result = skill.execute()
        assert result == "Hello, World!"

    def test_skill_with_custom_version(self) -> None:
        skill = UpperSkill()
        assert skill.metadata.version == "1.0.0"
        assert skill.metadata.tags == ["text", "transform"]


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

    def test_duplicate_registration_keeps_original_skill(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        with pytest.raises(ValueError, match="already registered"):
            registry.register(AlternateEchoSkill())

        assert registry.run("echo", text="kept") == "Echo: kept"
        assert len(registry) == 1

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

    def test_list_skills_preserves_registration_order(self) -> None:
        registry = SkillRegistry()
        registry.register(GreetSkill())
        registry.register(EchoSkill())
        registry.register(UpperSkill())

        assert [skill.name for skill in registry.list_skills()] == ["greet", "echo", "upper"]

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

    # ----- New edge-case and behavioral tests -----

    def test_list_skills_empty(self) -> None:
        registry = SkillRegistry()
        assert registry.list_skills() == []

    def test_list_skills_returns_metadata_objects(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        skills = registry.list_skills()
        assert len(skills) == 1
        assert isinstance(skills[0], SkillMetadata)
        assert skills[0].name == "echo"

    def test_contains_non_string(self) -> None:
        """The __contains__ signature accepts object; non-string should not raise."""
        registry = SkillRegistry()
        registry.register(EchoSkill())
        assert 42 not in registry  # type: ignore[operator]
        assert None not in registry  # type: ignore[operator]

    def test_run_with_no_kwargs(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        result = registry.run("echo")
        assert result == "Echo: "

    def test_run_forwards_multiple_keyword_arguments(self) -> None:
        registry = SkillRegistry()
        registry.register(PairSkill())

        assert registry.run("pair", left="alpha", right="omega") == "alpha:omega"

    def test_run_returns_correct_type(self) -> None:
        registry = SkillRegistry()
        registry.register(UpperSkill())
        result = registry.run("upper", text="hello")
        assert result == "HELLO"
        assert isinstance(result, str)

    def test_get_returns_same_instance(self) -> None:
        """Registry should return the same instance that was registered."""
        registry = SkillRegistry()
        skill = EchoSkill()
        registry.register(skill)
        retrieved = registry.get("echo")
        assert retrieved is skill

    def test_duplicate_error_message_contains_name(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        with pytest.raises(ValueError, match="echo"):
            registry.register(EchoSkill())

    def test_missing_skill_error_message_contains_name(self) -> None:
        registry = SkillRegistry()
        with pytest.raises(KeyError, match="nonexistent"):
            registry.run("nonexistent")

    def test_repr_with_multiple_skills(self) -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        registry.register(GreetSkill())
        registry.register(UpperSkill())
        assert "skills=3" in repr(registry)

    def test_multiple_registries_independent(self) -> None:
        """Two registry instances should be independent."""
        reg1 = SkillRegistry()
        reg2 = SkillRegistry()
        reg1.register(EchoSkill())
        assert len(reg1) == 1
        assert len(reg2) == 0

    def test_full_lifecycle(self) -> None:
        """Register multiple skills, run each, check listing, check membership."""
        registry = SkillRegistry()

        # Empty state
        assert len(registry) == 0
        assert registry.list_skills() == []

        # Register skills
        registry.register(EchoSkill())
        registry.register(GreetSkill())
        registry.register(UpperSkill())

        # Check membership
        assert "echo" in registry
        assert "greet" in registry
        assert "upper" in registry
        assert "nonexistent" not in registry
        assert len(registry) == 3

        # Run each
        assert registry.run("echo", text="test") == "Echo: test"
        assert registry.run("greet", name="World") == "Hello, World!"
        assert registry.run("upper", text="abc") == "ABC"

        # List metadata
        skills = registry.list_skills()
        assert len(skills) == 3
        names = {s.name for s in skills}
        assert names == {"echo", "greet", "upper"}
