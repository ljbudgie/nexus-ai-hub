# Integration Guide

This page explains how the four components of nexus-ai-hub interact with each other and how to get the most out of running them together.

---

## MemPalace inside Hermes Agent

MemPalace ships a first-class Hermes memory provider at `mempalace/hermes_provider.py`. When it is active, every Hermes session is automatically mined into your local palace on session end — no manual `mempalace mine` step needed.

### Activation

```bash
# Set once in config.yaml (setup.sh does this automatically)
hermes config set memory_provider mempalace
```

Hermes will load `mempalace/hermes_provider.py` from the plugin directory. On each session close the provider calls `mempalace mine` on the session transcript, adds it to the relevant wing, and makes it searchable immediately.

### Searching memory from inside Hermes

Because MemPalace also runs as an MCP server you can connect it as a tool source so the agent can call `mempalace_search` itself:

```bash
hermes mcp add mempalace -- python -m mempalace.mcp_server
```

Once connected the agent will automatically call `mempalace_search` when it needs to recall past context, without any manual prompting.

### Using the wake-up context

For local models that do not speak MCP, generate a compact context block before each session:

```bash
mempalace wake-up > /tmp/context.txt
# Prepend the file to your system prompt or paste it into the chat
```

This loads the most critical facts (~170 tokens in AAAK compression) so the model "remembers" your world without any API calls.

---

## OpenClaw Skills inside Hermes Agent

The `awesome-openclaw-skills` catalogue is the library; Hermes is the runtime.

### Installing skills

```bash
# Option A — ClawHub CLI (recommended)
clawhub install <skill-slug>

# Option B — Manual copy
cp -r awesome-openclaw-skills/<category>/<skill-folder>/ ~/.hermes/skills/
# Skills in ~/.hermes/skills/ are loaded automatically on next hermes start

# Option C — Workspace-local (only active for a specific project)
cp -r awesome-openclaw-skills/<category>/<skill-folder>/ ./skills/
```

### Enabling the Burgess human-review layer

Some skills in the catalogue handle high-stakes situations (accessibility requests, contract review, automated decisions). The Burgess upgrade wraps those skills with a mandatory human-review gate before the action is taken.

```bash
# Enable a Burgess-wrapped version of a skill
cp -r awesome-openclaw-skills/burgess/<skill-slug>/ ~/.hermes/skills/
```

The Burgess variant and the original share the same slug — copying the Burgess version shadows the original. Remove it to revert.

---

## Advocate Companion skills inside Hermes

The `advocate-companion/skills/` directory contains self-contained skill modules. These follow the same OpenClaw skill standard and can be loaded directly into Hermes:

```bash
# Load the contract-review skill into Hermes
cp -r advocate-companion/skills/contract-review-with-burgess/ ~/.hermes/skills/
```

Once loaded, ask Hermes to perform a contract review:

```
> Review this contract for reasonable adjustment clauses: <paste text>
```

The skill applies the Burgess binary ("Was a human able to personally review the specific facts of my case?") and flags any clause that needs human attention before proceeding.

---

## MemPalace as a standalone MCP server (Claude Desktop / Cursor / VS Code)

You do not need Hermes to use MemPalace. Any MCP-compatible client can connect directly:

```bash
# Claude Desktop
claude mcp add mempalace -- python -m mempalace.mcp_server

# Cursor / VS Code — add to your MCP settings JSON:
{
  "mempalace": {
    "command": "python",
    "args": ["-m", "mempalace.mcp_server"]
  }
}
```

The MCP server exposes 19 tools including `mempalace_search`, `mempalace_mine`, `mempalace_status`, and `mempalace_wake_up`.

---

## Full stack sequence diagram

```
User
 |
 |-- "hermes" --------> Hermes Agent (CLI / Telegram / Slack / ...)
                              |
                              |-- session start
                              |     |-- MemPalace wake-up (170 token context)
                              |
                              |-- user turn
                              |     |-- tools: search, code, browse
                              |     |-- skills: OpenClaw + Burgess-wrapped
                              |     |-- memory search: mempalace_search
                              |
                              |-- session end
                                    |-- MemPalace mines transcript
                                    |-- facts indexed for next session

Separately:
User --> advocate-companion (localhost:8080)
              |-- AI Co-Pilot (Gemini) generates adjustment message
              |-- Outlook integration reads/drafts replies
              |-- skills/contract-review-with-burgess/ applied on demand
              |-- Journal saved to LocalStorage (never leaves device)
```

---

## Keeping everything in sync

All components are git submodules. Update them together with:

```bash
git submodule update --remote --merge
```

Or individually:

```bash
git submodule update --remote --merge hermes-agent
git submodule update --remote --merge mempalace
git submodule update --remote --merge awesome-openclaw-skills
git submodule update --remote --merge advocate-companion
```

After updating Hermes or MemPalace, re-run the relevant install step:

```bash
cd hermes-agent && pip install -e . --quiet
cd mempalace    && pip install -e . --quiet
```
