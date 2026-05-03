"""Tests for the Hermes Agent module."""

from nexus_ai_hub.hermes_agent.agent import AgentConfig, Conversation, HermesAgent, Message


class TestAgentConfig:
    """Tests for AgentConfig defaults and custom values."""

    def test_defaults(self) -> None:
        config = AgentConfig()
        assert config.model == "default"
        assert config.max_turns == 10
        assert config.temperature == 0.7
        assert config.system_prompt == "You are Hermes, a helpful AI assistant."

    def test_custom_values(self) -> None:
        config = AgentConfig(
            model="gpt-4",
            max_turns=20,
            temperature=0.9,
            system_prompt="Custom prompt.",
        )
        assert config.model == "gpt-4"
        assert config.max_turns == 20
        assert config.temperature == 0.9
        assert config.system_prompt == "Custom prompt."

    def test_partial_override(self) -> None:
        config = AgentConfig(model="claude", temperature=0.0)
        assert config.model == "claude"
        assert config.max_turns == 10  # default preserved
        assert config.temperature == 0.0
        assert config.system_prompt == "You are Hermes, a helpful AI assistant."


class TestMessage:
    def test_creation(self) -> None:
        msg = Message(role="user", content="hi")
        assert msg.role == "user"
        assert msg.content == "hi"

    def test_empty_content(self) -> None:
        msg = Message(role="system", content="")
        assert msg.role == "system"
        assert msg.content == ""

    def test_multiline_content(self) -> None:
        msg = Message(role="user", content="line1\nline2\nline3")
        assert "\n" in msg.content
        assert msg.content.count("\n") == 2

    def test_special_characters(self) -> None:
        content = "Hello! @#$%^&*() 你好 émojis 🤖"
        msg = Message(role="user", content=content)
        assert msg.content == content


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

    def test_empty_history(self) -> None:
        conv = Conversation()
        assert conv.get_history() == []
        assert len(conv) == 0

    def test_clear_already_empty(self) -> None:
        conv = Conversation()
        conv.clear()
        assert len(conv) == 0
        assert conv.get_history() == []

    def test_history_returns_new_list(self) -> None:
        """Ensure get_history returns a new list each call (not a reference)."""
        conv = Conversation()
        conv.add_message("user", "hello")
        h1 = conv.get_history()
        h2 = conv.get_history()
        assert h1 == h2
        assert h1 is not h2

    def test_history_entries_are_copies(self) -> None:
        """Mutating returned history dictionaries should not mutate stored messages."""
        conv = Conversation()
        conv.add_message("user", "hello")
        history = conv.get_history()
        history[0]["content"] = "changed"
        history[0]["role"] = "assistant"

        assert conv.messages[0] == Message(role="user", content="hello")
        assert conv.get_history() == [{"role": "user", "content": "hello"}]

    def test_messages_field_default_factory(self) -> None:
        """Ensure each Conversation instance gets its own messages list."""
        conv1 = Conversation()
        conv2 = Conversation()
        conv1.add_message("user", "only in conv1")
        assert len(conv1) == 1
        assert len(conv2) == 0

    def test_bool_after_clear(self) -> None:
        conv = Conversation()
        conv.add_message("user", "hi")
        assert conv
        conv.clear()
        assert not conv

    def test_many_messages(self) -> None:
        conv = Conversation()
        for i in range(50):
            conv.add_message("user", f"msg {i}")
        assert len(conv) == 50
        history = conv.get_history()
        assert len(history) == 50
        assert history[0]["content"] == "msg 0"
        assert history[49]["content"] == "msg 49"


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

    def test_custom_config_instance_is_reused(self) -> None:
        config = AgentConfig(model="gpt-4", max_turns=5)
        agent = HermesAgent(config=config)
        assert agent.config is config

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

    def test_default_config_applied(self) -> None:
        agent = HermesAgent()
        assert agent.config.model == "default"
        assert agent.config.max_turns == 10
        assert agent.config.temperature == 0.7

    def test_chat_records_user_message(self) -> None:
        agent = HermesAgent()
        agent.chat("test input")
        history = agent.conversation.get_history()
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "test input"

    def test_chat_records_assistant_message(self) -> None:
        agent = HermesAgent()
        response = agent.chat("test input")
        history = agent.conversation.get_history()
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == response

    def test_chat_response_format(self) -> None:
        agent = HermesAgent()
        response = agent.chat("hello world")
        assert response == "[Hermes] Received: hello world"

    def test_chat_empty_input(self) -> None:
        agent = HermesAgent()
        response = agent.chat("")
        assert response == "[Hermes] Received: "
        assert len(agent.conversation) == 2

    def test_chat_preserves_surrounding_whitespace(self) -> None:
        agent = HermesAgent()
        response = agent.chat("  padded input  ")
        assert response == "[Hermes] Received:   padded input  "
        assert agent.conversation.get_history()[0]["content"] == "  padded input  "

    def test_reset_then_chat(self) -> None:
        agent = HermesAgent()
        agent.chat("first")
        agent.reset()
        agent.chat("second")
        history = agent.conversation.get_history()
        assert len(history) == 2
        assert history[0]["content"] == "second"

    def test_repr_before_chat(self) -> None:
        agent = HermesAgent()
        assert repr(agent) == "HermesAgent(model='default', turns=0)"

    def test_repr_with_custom_model(self) -> None:
        config = AgentConfig(model="llama-3")
        agent = HermesAgent(config=config)
        assert "llama-3" in repr(agent)

    def test_multiple_agents_independent(self) -> None:
        """Two agent instances should have independent conversations."""
        agent1 = HermesAgent()
        agent2 = HermesAgent()
        agent1.chat("hello from agent1")
        assert len(agent1.conversation) == 2
        assert len(agent2.conversation) == 0

    def test_chat_with_special_characters(self) -> None:
        agent = HermesAgent()
        response = agent.chat("Hello 🤖! @#$%")
        assert "Hello 🤖! @#$%" in response
