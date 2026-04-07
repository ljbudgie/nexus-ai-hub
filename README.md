<div align="center">

# nexus-ai-hub

### The ultimate AI helper hub

**Hermes Agent · MemPalace · 5,400+ OpenClaw Skills · Advocate Companion · The Burgess Principle**

[![CI](https://github.com/ljbudgie/nexus-ai-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/ljbudgie/nexus-ai-hub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

</div>

---

## What Is This?

**nexus-ai-hub** is a single repository that wires together five complementary AI tools into one cohesive stack.

It ships as **both** a usable Python package (installable with `pip install -e .`) **and** a hub that pins the five upstream projects as git submodules so you can run the full, production-grade versions side-by-side.

| Component | Role | Tech |
|-----------|------|------|
| [**Hermes Agent**](hermes-agent/) | Self-improving AI agent — skills, memory, 15 messaging platforms, 18 LLM providers | Python |
| [**MemPalace**](mempalace/) | Highest-scoring AI memory system — local, lossless, 96.6% recall | Python |
| [**Awesome OpenClaw Skills**](awesome-openclaw-skills/) | Curated catalogue of 5,400+ community skills for OpenClaw / Hermes | Markdown |
| [**Advocate Companion**](advocate-companion/) | Reasonable Adjustment Companion grounded in The Burgess Principle | React / TypeScript |
| [**The Burgess Principle**](burgess-principle/) | "Was a human able to review my case?" — the philosophy and framework behind the hub | Markdown |

---

## Features

- **Hermes Agent** — A conversational AI agent with multi-turn dialogue, tool
  orchestration, configurable behaviour, and a self-improving skills loop.
- **MemPalace** — Persistent memory store with tagging, search, and
  JSON import/export. Also ships a full palace-structured local memory system
  with 96.6% LongMemEval recall.
- **OpenClaw Skills** — A plugin-based skill registry that lets you register,
  discover, and execute modular capabilities. 5,400+ community skills available.
- **Advocate Companion** — AI-powered Reasonable Adjustment web UI grounded in
  The Burgess Principle; works offline and keeps all data in your browser.
- **The Burgess Principle** — The foundational framework that underpins the
  project. Includes templates, case studies, and key documents like `SOUL.md`
  and `FOR_AI_MODELS.md` that help AI assistants understand the "see the human
  first" philosophy.

---

## Project Structure

```
nexus-ai-hub/
|
+-- src/nexus_ai_hub/          # Python package (install with pip install -e .)
|   +-- hermes_agent/          # Conversational AI agent
|   |   +-- __init__.py
|   |   +-- agent.py
|   +-- mempalace/             # Long-term memory system
|   |   +-- __init__.py
|   |   +-- palace.py
|   +-- skills/                # Extensible skill/plugin system
|       +-- __init__.py
|       +-- registry.py
|
+-- tests/                     # Test suite
+-- docs/                      # Documentation
+-- pyproject.toml             # Project configuration
|
+-- hermes-agent/              # Submodule — full Hermes Agent (Python)
+-- mempalace/                 # Submodule — full MemPalace (Python)
+-- awesome-openclaw-skills/   # Submodule — 5,400+ skill catalogue (Markdown)
+-- advocate-companion/        # Submodule — Reasonable Adjustment UI (React)
+-- burgess-principle/         # Submodule — The Burgess Principle framework
+-- setup.sh                   # One-command bootstrap for the full stack
```

---

## Quick Start

### Python package (minimal)

```bash
git clone https://github.com/ljbudgie/nexus-ai-hub.git
cd nexus-ai-hub
pip install -e ".[dev]"
```

```python
from nexus_ai_hub import HermesAgent, MemPalace, BaseSkill, SkillMetadata, SkillRegistry

# Start a conversation with Hermes
agent = HermesAgent()
response = agent.chat("Hello, Hermes!")
print(response)

# Store and recall a memory
palace = MemPalace()
palace.store("user_preference", "dark mode", tags=["settings"])
memory = palace.recall("user_preference")
print(memory.content)  # "dark mode"

# Create and register a custom skill
class SummariseSkill(BaseSkill):
    metadata = SkillMetadata(name="summarise", description="Summarise text.")

    def execute(self, **kwargs: str) -> str:
        text = kwargs.get("text", "")
        return f"Summary of {len(text)} characters."

registry = SkillRegistry()
registry.register(SummariseSkill())
print(registry.run("summarise", text="Some long text here..."))
```

### Full stack (all four components)

```bash
# Clone with all submodules
git clone --recurse-submodules https://github.com/ljbudgie/nexus-ai-hub.git
cd nexus-ai-hub

# Install everything
./setup.sh
```

`setup.sh` installs Hermes Agent (with MemPalace pre-wired), seeds your skill library from the OpenClaw catalogue, and leaves you with the `hermes` CLI ready to use.

---

## Architecture

```
  +----------------------------------+
  |         Hermes Agent             |  <- one command to start: hermes
  |  +---------+  +---------------+  |
  |  |MemPalace|  |OpenClaw Skills|  |  <- memory + 5,400 skills
  |  +---------+  +---------------+  |
  +---------------+------------------+
                  | Burgess Principle
                  v
  +----------------------------------+
  |      Advocate Companion          |  <- web UI for self-advocacy
  |  React . Supabase . Gemini AI    |
  +----------------------------------+

  +----------------------------------+
  |      The Burgess Principle       |  <- foundational philosophy & framework
  |  SOUL.md . FOR_AI_MODELS.md      |
  |  templates/ . case-studies/      |
  +----------------------------------+
```

See [docs/integration.md](docs/integration.md) for a full sequence diagram and per-component wiring guide.

---

## Development

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

---

## Manual Component Setup

### Hermes Agent + MemPalace

```bash
cd hermes-agent
./setup-hermes.sh      # installs hermes CLI, all dependencies, seeds skills
hermes setup           # configure API keys and providers
hermes config set memory_provider mempalace
```

### OpenClaw Skills

```bash
# Via ClawHub CLI
clawhub install <skill-slug>

# Or copy manually
cp -r awesome-openclaw-skills/<category>/<skill>/ ~/.hermes/skills/
```

### Advocate Companion

```bash
cd advocate-companion
npm install
npm run dev            # http://localhost:8080
```

---

## Updating Submodules

```bash
# Pull latest commits for all submodules
git submodule update --remote --merge

# Or update a single component
git submodule update --remote --merge hermes-agent
```

---

## Roadmap

- [ ] LLM backend integration for Hermes Agent (Python package)
- [ ] Vector-based semantic search for MemPalace (Python package)
- [ ] Built-in skill library (web search, code execution, file I/O, etc.)
- [ ] CLI interface
- [ ] REST API server
- [ ] Conversation persistence and replay
- [ ] Skill auto-discovery from installed packages

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

- **nexus-ai-hub** (this repository) — MIT — see [LICENSE](LICENSE)
- **Hermes Agent** — MIT ([hermes-agent/LICENSE](hermes-agent/LICENSE))
- **MemPalace** — MIT ([mempalace/LICENSE](mempalace/LICENSE))
- **Awesome OpenClaw Skills** — MIT ([awesome-openclaw-skills/LICENSE](awesome-openclaw-skills/LICENSE))
- **Advocate Companion** — MIT with additional terms for *The Burgess Principle* content ([advocate-companion/LICENSE](advocate-companion/LICENSE))
- **The Burgess Principle** — MIT (doctrine); certification mark for commercial standard ([burgess-principle/LICENSE.md](burgess-principle/LICENSE.md))

---

## Acknowledgements

- [Nous Research](https://nousresearch.com) — Hermes Agent
- [milla-jovovich](https://github.com/milla-jovovich) — MemPalace
- [VoltAgent / ClawHub](https://clawskills.sh) — OpenClaw Skills registry
- [The Burgess Principle](https://github.com/ljbudgie/burgess-principle) — accessibility advocacy framework
