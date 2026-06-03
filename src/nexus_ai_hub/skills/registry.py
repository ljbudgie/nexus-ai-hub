"""Skill registry and base classes for the OpenClaw skill system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from nexus_ai_hub.burgess.gate import BurgessBlockedError, BurgessGate, Decision
from nexus_ai_hub.core import BurgessContext

__all__ = ["BaseSkill", "SkillMetadata", "SkillRegistry"]


@dataclass
class SkillMetadata:
    """Metadata describing a registered skill.

    ``domain`` and ``impact_class`` feed the Burgess gate when a registry is
    constructed with one. They default to a low-stakes ``general`` skill so that
    informational skills run without a review gate; declare a high-impact domain
    (or ``impact_class="high"``) for skills that can affect a person.
    """

    name: str
    description: str
    version: str = "0.1.0"
    tags: list[str] = field(default_factory=list)
    domain: str = "general"
    impact_class: str = "low"


class BaseSkill(ABC):
    """Abstract base class for all OpenClaw skills.

    Every skill must implement the ``execute`` method and provide metadata.

    Example::

        class GreetSkill(BaseSkill):
            metadata = SkillMetadata(
                name="greet",
                description="Greet the user by name.",
            )

            def execute(self, **kwargs: str) -> str:
                name = kwargs.get("name", "World")
                return f"Hello, {name}!"
    """

    metadata: SkillMetadata

    @abstractmethod
    def execute(self, **kwargs: str) -> str:
        """Run the skill with the provided keyword arguments.

        Args:
            **kwargs: Skill-specific parameters.

        Returns:
            The skill's output as a string.
        """


class SkillRegistry:
    """Registry that manages available skills.

    Skills are registered by name and can be looked up or listed.

    Example::

        registry = SkillRegistry()
        registry.register(GreetSkill())
        result = registry.run("greet", name="Alice")

    When constructed with a :class:`~nexus_ai_hub.burgess.gate.BurgessGate`, the
    registry routes every execution through the gate first. High-impact skills
    classified NULL are blocked with :class:`BurgessBlockedError` unless an
    ``approver`` is supplied to :meth:`run`.
    """

    def __init__(self, *, gate: BurgessGate | None = None) -> None:
        self._skills: dict[str, BaseSkill] = {}
        self._gate = gate

    def register(self, skill: BaseSkill) -> None:
        """Register a skill in the registry.

        Args:
            skill: A skill instance to register.

        Raises:
            ValueError: If a skill with the same name is already registered.
        """
        name = skill.metadata.name
        if name in self._skills:
            raise ValueError(f"Skill '{name}' is already registered.")
        self._skills[name] = skill

    def get(self, name: str) -> BaseSkill | None:
        """Retrieve a skill by name.

        Args:
            name: The registered skill name.

        Returns:
            The skill instance if found, otherwise None.
        """
        return self._skills.get(name)

    def run(self, skill_name: str, *, approver: str | None = None, **kwargs: str) -> str:
        """Execute a registered skill by name.

        If the registry was constructed with a Burgess gate, the skill is
        classified before it runs. A skill classified NULL is blocked unless
        ``approver`` is supplied, in which case a human-review record is written
        to the gate's ledger before execution proceeds.

        Args:
            skill_name: The registered skill name.
            approver: A stable identifier for the human releasing a NULL skill.
            **kwargs: Arguments forwarded to the skill's execute method.

        Returns:
            The skill's output string.

        Raises:
            KeyError: If the skill is not found in the registry.
            BurgessBlockedError: If a NULL skill is run without an ``approver``.
        """
        skill = self._skills.get(skill_name)
        if skill is None:
            raise KeyError(f"Skill '{skill_name}' not found in registry.")
        if self._gate is not None:
            meta = skill.metadata
            context = BurgessContext(
                domain=meta.domain,
                facts=f"Execute skill {skill_name!r}: {meta.description}",
                metadata={"impact_class": meta.impact_class},
            )
            record = self._gate.evaluate(f"skill:{skill_name}", context)
            if record.decision == Decision.NULL.value:
                if approver is None:
                    raise BurgessBlockedError(record)
                self._gate.require_human(record, approver)
        return skill.execute(**kwargs)

    def list_skills(self) -> list[SkillMetadata]:
        """Return metadata for all registered skills."""
        return [s.metadata for s in self._skills.values()]

    def __len__(self) -> int:
        """Return the number of registered skills."""
        return len(self._skills)

    def __contains__(self, name: object) -> bool:
        """Check whether a skill name is registered."""
        return name in self._skills

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"SkillRegistry(skills={len(self._skills)})"
