# 🧠 Nexus AI Hub

[![CI](https://github.com/ljbudgie/nexus-ai-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/ljbudgie/nexus-ai-hub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**The ultimate AI helper hub — Hermes Agent + MemPalace + OpenClaw Skills**

Nexus AI Hub brings together a conversational AI agent, persistent memory, and a
powerful extensible skill system into a single, modular platform.

---

## ✨ Features

- **Hermes Agent** — A conversational AI agent with multi-turn dialogue, tool
  orchestration, and configurable behaviour.
- **MemPalace** — Persistent memory store with tagging, search, and
  JSON import/export for long-term knowledge retention across sessions.
- **OpenClaw Skills** — A plugin-based skill registry that lets you register,
  discover, and execute modular capabilities.

## 📁 Project Structure

```
nexus-ai-hub/
├── src/nexus_ai_hub/
│   ├── hermes_agent/      # Conversational AI agent
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── mempalace/          # Long-term memory system
│   │   ├── __init__.py
│   │   └── palace.py
│   └── skills/             # Extensible skill/plugin system
│       ├── __init__.py
│       └── registry.py
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/ljbudgie/nexus-ai-hub.git
cd nexus-ai-hub

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Quick Example

```python
from nexus_ai_hub.hermes_agent.agent import HermesAgent
from nexus_ai_hub.mempalace.palace import MemPalace
from nexus_ai_hub.skills.registry import BaseSkill, SkillMetadata, SkillRegistry

# Start a conversation with Hermes
agent = HermesAgent()
response = agent.chat("Hello, Hermes!")
print(response)

# Store a memory
palace = MemPalace()
palace.store("user_preference", "dark mode", tags=["settings"])
memory = palace.recall("user_preference")
print(memory.content)  # "dark mode"

# Create and register a custom skill
class SummariseSkill(BaseSkill):
    metadata = SkillMetadata(name="summarise", description="Summarise text.")

    def execute(self, **kwargs):
        text = kwargs.get("text", "")
        return f"Summary of {len(text)} characters."

registry = SkillRegistry()
registry.register(SummariseSkill())
print(registry.run("summarise", text="Some long text here..."))
```

## 🧪 Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=nexus_ai_hub --cov-report=term-missing
```

### Linting

```bash
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## 🗺️ Roadmap

- [ ] LLM backend integration for Hermes Agent
- [ ] Vector-based semantic search for MemPalace
- [ ] Built-in skill library (web search, code execution, file I/O, etc.)
- [ ] CLI interface
- [ ] REST API server
- [ ] Conversation persistence and replay
- [ ] Skill auto-discovery from installed packages

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file
for details.
