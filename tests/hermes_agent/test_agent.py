"""Tests for the Hermes Agent module."""

from nexus_ai_hub.hermes_agent.agent import AgentConfig, Conversation, HermesAgent, Message


class TestMessage:
    def test_creation(self) -> None:
        msg = Message(role="user", content="hi")
        assert msg.role == "user"
        assert msg.content == "hi"


class TestConversation:
    def test_add_and_get_history(self) -> None:
        conv = Conversation()
        conv.add_message("user", "hello")
        conv.add_message("assistant", "hi there")
        history = conv.get_history()
        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "hello"}
        assert history[1] == {"role": "assistant", "content": "hi there"}

    def test_clear(self) -> None:
        conv = Conversation()
        conv.add_message("user", "hello")
        conv.clear()
        assert conv.get_history() == []

    def test_len(self) -> None:
        conv = Conversation()
        assert len(conv) == 0
        conv.add_message("user", "hello")
        assert len(conv) == 1
        conv.add_message("assistant", "hi")
        assert len(conv) == 2

    def test_bool(self) -> None:
        conv = Conversation()
        assert not conv
        conv.add_message("user", "hello")
        assert conv


class TestHermesAgent:
    def test_chat_returns_response(self) -> None:
        agent = HermesAgent()
        response = agent.chat("ping")
        assert "ping" in response

    def test_custom_config(self) -> None:
        config = AgentConfig(model="gpt-4", max_turns=5)
        agent = HermesAgent(config=config)
        assert agent.config.model == "gpt-4"
        assert agent.config.max_turns == 5

    def test_conversation_history_grows(self) -> None:
        agent = HermesAgent()
        agent.chat("first")
        agent.chat("second")
        history = agent.conversation.get_history()
        assert len(history) == 4  # 2 user + 2 assistant messages

    def test_reset_clears_history(self) -> None:
        agent = HermesAgent()
        agent.chat("hello")
        agent.reset()
        assert agent.conversation.get_history() == []

    def test_repr(self) -> None:
        agent = HermesAgent()
        assert "HermesAgent" in repr(agent)
        assert "default" in repr(agent)
        agent.chat("hello")
        assert "turns=2" in repr(agent)
