<div align="center">

# nexus-ai-hub

### The ultimate AI helper hub

**Hermes Agent · MemPalace · 5,400+ OpenClaw Skills · Advocate Companion**

</div>

---

## What Is This?

**nexus-ai-hub** is a single repository that wires together four complementary AI tools into one cohesive stack:

| Component | Role | Tech |
|-----------|------|------|
| [**Hermes Agent**](hermes-agent/) | Self-improving AI agent — skills, memory, 15 messaging platforms, 18 LLM providers | Python |
| [**MemPalace**](mempalace/) | Highest-scoring AI memory system — local, lossless, 96.6% recall | Python |
| [**Awesome OpenClaw Skills**](awesome-openclaw-skills/) | Curated catalogue of 5,400+ community skills for OpenClaw / Hermes | Markdown |
| [**Advocate Companion**](advocate-companion/) | Reasonable Adjustment Companion grounded in The Burgess Principle | React / TypeScript |

Each component lives as a **git submodule** so you always track the upstream source. You can use all four together or pull in only the pieces you need.

---

## Architecture

```
nexus-ai-hub/
|
+-- hermes-agent/          <- AI agent brain (skills, tools, gateway, multi-platform)
|   +-- plugins/memory/    <- Pluggable memory backends
|
+-- mempalace/             <- AI memory layer -- mine + search conversations & projects
|   +-- mempalace/hermes_provider.py  <- Drop-in Hermes memory plugin
|
+-- awesome-openclaw-skills/  <- 5,400+ curated skills -- install any with clawhub
|   +-- burgess/           <- Burgess Principle upgrade skills (human-review gate)
|
+-- advocate-companion/    <- Web UI -- reasonable-adjustment Co-Pilot + email integration
    +-- skills/            <- Self-contained advocacy skills (contract review, etc.)
```

### How the pieces connect

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
```

1. **Hermes Agent** is the agent runtime. It manages conversations, calls tools, and runs skills.
2. **MemPalace** plugs into Hermes as a memory provider (`hermes_provider.py`). Every session is automatically mined and made searchable — 96.6% recall, entirely local.
3. **Awesome OpenClaw Skills** is the catalogue you browse to install skills into Hermes (`clawhub install <skill-slug>` or copy to `~/.hermes/skills/`). The `burgess/` sub-folder adds a human-review gate to high-stakes skills.
4. **Advocate Companion** is a standalone React web app that uses The Burgess Principle to generate legally-grounded reasonable-adjustment messages. Its `skills/` folder contains focused skills (contract review, follow-up threads, etc.) that can also run inside Hermes.

---

## Quick Start

### Prerequisites

- **Python >= 3.11** (Hermes Agent + MemPalace)
- **Node.js >= 18** (Advocate Companion)
- **git** with submodule support

### One-command setup

```bash
# Clone with all submodules
git clone --recurse-submodules https://github.com/ljbudgie/nexus-ai-hub.git
cd nexus-ai-hub

# Install everything
./setup.sh
```

`setup.sh` installs Hermes Agent (with MemPalace pre-wired), seeds your skill library from the OpenClaw catalogue, and leaves you with the `hermes` CLI ready to use.

### Manual setup (component by component)

#### 1 — Hermes Agent + MemPalace

```bash
cd hermes-agent
./setup-hermes.sh      # installs hermes CLI, all dependencies, seeds skills
hermes setup           # configure API keys and providers
```

Enable MemPalace as the memory provider:

```bash
# Connect MemPalace MCP server to Claude / any MCP client
claude mcp add mempalace -- python -m mempalace.mcp_server

# Or register it as a Hermes memory plugin
hermes config set memory_provider mempalace
```

Mine your existing conversations and projects into MemPalace:

```bash
cd mempalace
pip install mempalace
mempalace init ~/projects/my-project
mempalace mine ~/projects/my-project
mempalace mine ~/chats/ --mode convos
```

#### 2 — Install OpenClaw Skills into Hermes

Browse the catalogue in [`awesome-openclaw-skills/README.md`](awesome-openclaw-skills/README.md), then install:

```bash
# Via ClawHub CLI
clawhub install <skill-slug>

# Or copy manually
cp -r awesome-openclaw-skills/<category>/<skill>/ ~/.hermes/skills/

# Enable the Burgess human-review layer for high-stakes skills
cp -r awesome-openclaw-skills/burgess/<skill>/ ~/.hermes/skills/
```

#### 3 — Advocate Companion (web UI)

```bash
cd advocate-companion
npm install
npm run dev            # http://localhost:8080
```

Set your Gemini API key in `.env` (see `advocate-companion/.env` for the required variables) then open the browser to start generating legally-grounded reasonable-adjustment messages.

---

## Components In Detail

### Hermes Agent

The self-improving AI agent built by [Nous Research](https://nousresearch.com). Key features:

- **18 LLM providers** — Anthropic, OpenAI, Gemini, OpenRouter, Nous Portal (400+ models), and more
- **15 messaging platforms** — Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, SMS, and more
- **Pluggable memory** — swap in MemPalace, Honcho, Mem0, or any custom backend
- **Skills system** — install from the OpenClaw catalogue or write your own
- **Runs anywhere** — local, Docker, SSH, Modal (serverless), Daytona
- **Burgess Principle** — built-in human-impact awareness; flags changes affecting real people before shipping

```bash
hermes              # start chatting
hermes model        # choose LLM provider
hermes skills       # manage skills
hermes gateway      # start messaging gateway
```

Full docs: [hermes-agent/README.md](hermes-agent/README.md)

---

### MemPalace

The highest-scoring open-source AI memory system on LongMemEval. Key features:

- **96.6% recall** (R@5, zero API calls) — 100% with optional Haiku rerank
- **Palace structure** — wings -> rooms -> closets -> drawers; +34% retrieval vs flat storage
- **AAAK compression** — lossless 30x compression; loads months of context in ~170 tokens
- **Three mining modes** — `projects` (code/docs), `convos` (Claude/ChatGPT/Slack exports), `general` (auto-classifies decisions, preferences, milestones)
- **Fully local** — ChromaDB on your machine, no cloud calls required
- **MCP server** — 19 tools for Claude Desktop, Cursor, VS Code, and any MCP client
- **Hermes plugin** — `hermes_provider.py` registers MemPalace as a Hermes memory backend

```bash
pip install mempalace
mempalace init ~/projects/myapp
mempalace mine ~/chats/ --mode convos
mempalace search "why did we switch to GraphQL"
mempalace wake-up > context.txt   # load into local model system prompt
```

Full docs: [mempalace/README.md](mempalace/README.md)

---

### Awesome OpenClaw Skills — Burgess Edition

A curated catalogue of **5,400+ community-built OpenClaw skills**, filtered for quality, safety, and relevance. This fork adds the optional Burgess Principle upgrade layer.

- **5,400+ skills** — Filtered from 13,700+ in the public ClawHub registry (spam, duplicates, malicious entries removed)
- **Organised by category** — browse [`awesome-openclaw-skills/categories/`](awesome-openclaw-skills/categories/)
- **Burgess upgrade layer** — skills that touch accessibility, contracts, privacy, or automated decisions get an optional human-review gate; lives in [`burgess/`](awesome-openclaw-skills/burgess/) and is fully opt-in

Install any skill:

```bash
clawhub install <skill-slug>                              # via ClawHub CLI
cp -r awesome-openclaw-skills/<path>/ ~/.hermes/skills/   # manual copy
```

Full catalogue: [awesome-openclaw-skills/README.md](awesome-openclaw-skills/README.md)

---

### Advocate Companion

An AI-powered Reasonable Adjustment Companion grounded in [The Burgess Principle](https://github.com/ljbudgie/burgess-principle). Key features:

- **31+ predefined adjustments** — ADHD, anxiety, autism, chronic pain, mobility, and more
- **21 supported countries** — country-specific legal references (Equality Act 2010, ADA, etc.)
- **AI Co-Pilot** — context-aware message generation via Google Gemini
- **Outlook / Hotmail integration** — read incoming emails, draft legally-grounded replies
- **Privacy-first** — all personal data stays in your browser (LocalStorage only)
- **Offline mode** — curated Burgess Principle templates always available without an internet connection
- **PDF export + Response Journal** — full record of every adjustment request you have made

```bash
cd advocate-companion
npm install && npm run dev   # http://localhost:8080
```

Full docs: [advocate-companion/README.md](advocate-companion/README.md)

---

## Updating Submodules

```bash
# Pull latest commits for all submodules
git submodule update --remote --merge

# Or update a single component
git submodule update --remote --merge hermes-agent
```

---

## Contributing

Contributions to nexus-ai-hub (integration layer, setup scripts, documentation) are welcome. For component-level contributions see each submodule's own `CONTRIBUTING.md`.

---

## License

- **nexus-ai-hub** (this repository) — MIT
- **Hermes Agent** — MIT ([hermes-agent/LICENSE](hermes-agent/LICENSE))
- **MemPalace** — MIT ([mempalace/LICENSE](mempalace/LICENSE))
- **Awesome OpenClaw Skills** — MIT ([awesome-openclaw-skills/LICENSE](awesome-openclaw-skills/LICENSE))
- **Advocate Companion** — MIT with additional terms for *The Burgess Principle* content ([advocate-companion/LICENSE](advocate-companion/LICENSE))

---

## Acknowledgements

- [Nous Research](https://nousresearch.com) — Hermes Agent
- [milla-jovovich](https://github.com/milla-jovovich) — MemPalace
- [VoltAgent / ClawHub](https://clawskills.sh) — OpenClaw Skills registry
- [The Burgess Principle](https://github.com/ljbudgie/burgess-principle) — accessibility advocacy framework
