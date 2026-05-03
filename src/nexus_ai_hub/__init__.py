"""Nexus AI Hub — The ultimate AI helper hub."""

from nexus_ai_hub.core import (
    BurgessContext,
    BurgessIntegration,
    HapticProfile,
    MirrorIntegration,
    MirrorRights,
    NexusHub,
    OpenHearIntegration,
)
from nexus_ai_hub.hermes_agent.agent import AgentConfig, Conversation, HermesAgent, Message
from nexus_ai_hub.mempalace.palace import Memory, MemPalace
from nexus_ai_hub.skills.registry import BaseSkill, SkillMetadata, SkillRegistry

__version__ = "0.1.0"

__all__ = [
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
]
