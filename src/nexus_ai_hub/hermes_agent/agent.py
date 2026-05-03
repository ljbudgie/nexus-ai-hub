"""Hermes Agent core implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["AgentConfig", "Conversation", "HermesAgent", "Message"]


@dataclass
class AgentConfig:
    """Configuration for the Hermes Agent."""

    model: str = "default"
    max_turns: int = 10
    temperature: float = 0.7
    system_prompt: str = "You are Hermes, a helpful AI assistant."


@dataclass
class Message:
    """A single message in a conversation."""

    role: str
    content: str


@dataclass
class Conversation:
    """Manages a multi-turn conversation."""

    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation history."""
        self.messages.append(Message(role=role, content=content))

    def get_history(self) -> list[dict[str, str]]:
        """Return conversation history as a list of dicts."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()

    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)

    def __bool__(self) -> bool:
        """Return True if there are any messages."""
        return bool(self.messages)


class HermesAgent:
    """The Hermes conversational AI agent.

    Hermes is designed to assist users by orchestrating tools, maintaining
    conversation context, and leveraging the MemPalace for long-term memory.

    Example::

        agent = HermesAgent()
        response = agent.chat("Hello, Hermes!")
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.conversation = Conversation()

    def chat(self, user_input: str, context: object | None = None) -> str:
        """Process user input and return a response.

        Args:
            user_input: The user's message.
            context: Optional ecosystem context for the response.

        Returns:
            The agent's response string.
        """
        self.conversation.add_message("user", user_input)
        # Placeholder — integrate with an LLM backend
        response = f"[Hermes] Received: {user_input}" + (
            f" | Context: {context!r}" if context is not None else ""
        )
        self.conversation.add_message("assistant", response)
        return response

    def reset(self) -> None:
        """Reset the conversation state."""
        self.conversation.clear()

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return (
            f"HermesAgent(model={self.config.model!r}, "
            f"turns={len(self.conversation)})"
        )
