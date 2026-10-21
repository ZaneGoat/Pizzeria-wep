#!/usr/bin/env bash
# ==============================================================================
# Pizza Time — Automated Installation & Setup Script
# Repository: https://github.com/ZaneGoat/Pizzeria-wep.git
# ==============================================================================

set -euo pipefail

# Terminal Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUN_SERVER=false
SEED_SAMPLES=true
PORT=5000

print_usage() {
    echo -e "${BOLD}Usage:${NC} ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --run             Start the Flask server immediately after installation"
    echo "  --no-samples      Skip seeding sample Moroccan clients and orders"
    echo "  --port <PORT>     Specify port when using --run (default: 5000)"
    echo "  -h, --help        Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --run)
            RUN_SERVER=true
            shift
            ;;
        --no-samples)
            SEED_SAMPLES=false
            shift
            ;;
        --port)
            PORT="${2:-5000}"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}[!] Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

echo -e "${CYAN}${BOLD}"
echo "=================================================================="
echo "          PIZZA TIME — INSTALLATION & CONFIGURATION (v2.0)        "
echo "=================================================================="
echo -e "${NC}"

# 1. Check Python 3
echo -e "${BLUE}[1/5]${NC} Checking Python 3 environment..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed. Please install python3 first.${NC}"
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo -e "      ${GREEN}[OK] Found Python ${PY_VER}${NC}"

# 2. Create Virtual Environment
echo -e "${BLUE}[2/5]${NC} Setting up Python virtual environment (venv)..."
if [[ ! -d "venv" ]]; then
    if ! python3 -m venv venv; then
        echo -e "${YELLOW}[!] python3-venv missing. Attempting to install via apt...${NC}"
        sudo apt-get update && sudo apt-get install -y python3-venv
        python3 -m venv venv
    fi
    echo -e "      ${GREEN}[OK] Virtual environment created at ./venv${NC}"
else
    echo -e "      ${GREEN}[OK] Existing virtual environment found at ./venv${NC}"
fi

# Activate venv
# shellcheck disable=SC1091
source venv/bin/activate

# 3. Install Dependencies
echo -e "${BLUE}[3/5]${NC} Installing Python dependencies from requirements.txt..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
echo -e "      ${GREEN}[OK] Dependencies installed successfully${NC}"

# 4. Initialize Database & Default Accounts
echo -e "${BLUE}[4/5]${NC} Initializing SQLite database and default accounts..."
flask --app app init-db
echo -e "      ${GREEN}[OK] Database initialized (admin/admin123 & staff/staff123)${NC}"

# 5. Seed Menu & Sample Orders
echo -e "${BLUE}[5/5]${NC} Seeding menu items..."
python seed_menu.py

if [[ "$SEED_SAMPLES" == true ]]; then
    ORDER_COUNT=$(python -c "from app import app; from models import Commande;
with app.app_context(): print(Commande.query.count())")
    if [[ "$ORDER_COUNT" -eq 0 ]]; then
        echo -e "      Seeding sample clients & orders..."
        python seed_samples.py
    else
        echo -e "      ${GREEN}[OK] Database already has ${ORDER_COUNT} order(s) (skipping duplicate sample seed)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}${BOLD}==================================================================${NC}"
echo -e "${GREEN}${BOLD}  INSTALLATION COMPLETE${NC}"
echo -e "${GREEN}${BOLD}==================================================================${NC}"
echo -e "  Storefront URL:    http://127.0.0.1:${PORT}/"
echo -e "  Admin Dashboard:   http://127.0.0.1:${PORT}/login  (${CYAN}admin${NC} / ${CYAN}admin123${NC})"
echo -e "  Kitchen KDS:       http://127.0.0.1:${PORT}/login  (${CYAN}staff${NC} / ${CYAN}staff123${NC})"
echo ""
echo -e "  ${BOLD}To start the server manually:${NC}"
echo -e "    source venv/bin/activate && flask --app app run --port ${PORT}"
echo -e "  ${BOLD}Or run directly:${NC}"
echo -e "    ./install.sh --run"
echo -e "${GREEN}${BOLD}==================================================================${NC}"

if [[ "$RUN_SERVER" == true ]]; then
    echo -e "\n${YELLOW}Starting Pizza Time on http://127.0.0.1:${PORT} ...${NC}"
    exec flask --app app --debug run --host=0.0.0.0 --port="$PORT"
fi
