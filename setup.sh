#!/usr/bin/env bash
# =============================================================================
# nexus-ai-hub — Unified Setup Script
# =============================================================================
# Installs:
#   1. Hermes Agent (Python CLI + all dependencies)
#   2. MemPalace    (Python package + Hermes memory plugin wired in)
#   3. Advocate Companion dependencies (Node.js packages)
#
# The Awesome OpenClaw Skills catalogue is already available in the
# awesome-openclaw-skills/ submodule — no installation needed.
#
# Usage:
#   ./setup.sh [--skip-advocate]
#
# Options:
#   --skip-advocate   Skip the Advocate Companion Node.js install
# =============================================================================

set -e

SKIP_ADVOCATE=false
for arg in "$@"; do
    case $arg in
        --skip-advocate) SKIP_ADVOCATE=true ;;
    esac
done

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${CYAN}nexus-ai-hub setup${NC}"
echo "=============================="
echo ""

# =============================================================================
# Verify submodules are populated
# =============================================================================

for mod in hermes-agent mempalace awesome-openclaw-skills advocate-companion; do
    if [ ! -f "$SCRIPT_DIR/$mod/.git" ] && [ ! -d "$SCRIPT_DIR/$mod/.git" ]; then
        # Submodule directory exists but may not be initialised yet
        if [ -z "$(ls -A "$SCRIPT_DIR/$mod" 2>/dev/null)" ]; then
            echo -e "${CYAN}->  Initialising git submodules...${NC}"
            git -C "$SCRIPT_DIR" submodule update --init --recursive
            break
        fi
    fi
done

echo -e "${GREEN}v${NC} Submodules present"

# =============================================================================
# 1. Hermes Agent
# =============================================================================

echo ""
echo -e "${CYAN}[1/3] Installing Hermes Agent...${NC}"

if [ ! -f "$SCRIPT_DIR/hermes-agent/setup-hermes.sh" ]; then
    echo -e "${RED}x${NC} hermes-agent/setup-hermes.sh not found."
    echo "    Make sure the submodule is populated: git submodule update --init"
    exit 1
fi

bash "$SCRIPT_DIR/hermes-agent/setup-hermes.sh"

echo -e "${GREEN}v${NC} Hermes Agent installed"

# =============================================================================
# 2. MemPalace
# =============================================================================

echo ""
echo -e "${CYAN}[2/3] Installing MemPalace...${NC}"

# Prefer the local submodule over PyPI so we stay in sync
if [ -d "$SCRIPT_DIR/mempalace" ] && [ -f "$SCRIPT_DIR/mempalace/pyproject.toml" ]; then
    # Install into the same venv that Hermes created
    VENV_PIP="$SCRIPT_DIR/hermes-agent/venv/bin/pip"
    if [ -f "$VENV_PIP" ]; then
        "$VENV_PIP" install -e "$SCRIPT_DIR/mempalace" --quiet
    else
        pip install -e "$SCRIPT_DIR/mempalace" --quiet
    fi
    echo -e "${GREEN}v${NC} MemPalace installed from submodule (editable)"
else
    echo -e "${YELLOW}!${NC} mempalace submodule not populated — installing from PyPI"
    pip install mempalace --quiet
    echo -e "${GREEN}v${NC} MemPalace installed from PyPI"
fi

# Wire MemPalace into Hermes as the default memory provider
HERMES_CONFIG_DIR="${HERMES_HOME:-$HOME/.hermes}"
HERMES_CONFIG="$HERMES_CONFIG_DIR/config.yaml"
mkdir -p "$HERMES_CONFIG_DIR"

if [ -f "$HERMES_CONFIG" ]; then
    if grep -q "memory_provider" "$HERMES_CONFIG" 2>/dev/null; then
        echo -e "${YELLOW}!${NC} memory_provider already set in $HERMES_CONFIG — skipping"
    else
        echo "" >> "$HERMES_CONFIG"
        echo "memory_provider: mempalace" >> "$HERMES_CONFIG"
        echo -e "${GREEN}v${NC} MemPalace set as Hermes memory provider in config.yaml"
    fi
else
    echo "memory_provider: mempalace" > "$HERMES_CONFIG"
    echo -e "${GREEN}v${NC} Created $HERMES_CONFIG with MemPalace as memory provider"
fi

# =============================================================================
# 3. Advocate Companion (optional)
# =============================================================================

if [ "$SKIP_ADVOCATE" = false ]; then
    echo ""
    echo -e "${CYAN}[3/3] Installing Advocate Companion (Node.js)...${NC}"

    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}!${NC} Node.js not found — skipping Advocate Companion."
        echo "    Install Node.js >= 18 from https://nodejs.org/ and re-run:"
        echo "    cd advocate-companion && npm install"
    elif [ -f "$SCRIPT_DIR/advocate-companion/package.json" ]; then
        cd "$SCRIPT_DIR/advocate-companion"
        npm install --silent
        cd "$SCRIPT_DIR"
        echo -e "${GREEN}v${NC} Advocate Companion dependencies installed"
        echo "    Run: cd advocate-companion && npm run dev"
    else
        echo -e "${YELLOW}!${NC} advocate-companion/package.json not found — skipping."
    fi
else
    echo ""
    echo -e "${YELLOW}!${NC} [3/3] Skipping Advocate Companion (--skip-advocate)"
fi

# =============================================================================
# Done
# =============================================================================

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Reload your shell (or open a new terminal):"
echo "     source ~/.bashrc   # or ~/.zshrc"
echo ""
echo "  2. Configure API keys:"
echo "     hermes setup"
echo ""
echo "  3. Start chatting:"
echo "     hermes"
echo ""
echo "  4. Mine your conversations into MemPalace:"
echo "     mempalace init ~/projects/myapp"
echo "     mempalace mine ~/chats/ --mode convos"
echo ""
echo "  5. Browse 5,400+ OpenClaw skills:"
echo "     cat awesome-openclaw-skills/README.md | less"
echo "     clawhub install <skill-slug>"
echo ""
if [ "$SKIP_ADVOCATE" = false ] && command -v node &> /dev/null; then
    echo "  6. Launch the Advocate Companion web UI:"
    echo "     cd advocate-companion && npm run dev"
    echo "     # then open http://localhost:8080"
    echo ""
fi
