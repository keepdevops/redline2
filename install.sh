#!/bin/bash
set -e

# REDLINE Install Script
# Installs dependencies and sets up the environment in-place.
# Usage: ./install.sh [--web-only] [--skip-env] [--help]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_MIN="3.11"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --web-only    Skip GUI (Tkinter) dependencies"
    echo "  --skip-env    Skip .env setup"
    echo "  --help        Show this message"
}

# ── Argument parsing ────────────────────────────────────────────────────────
WEB_ONLY=false
SKIP_ENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --web-only)   WEB_ONLY=true; shift ;;
        --skip-env)   SKIP_ENV=true; shift ;;
        --help)       usage; exit 0 ;;
        *) error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# ── Safety check ────────────────────────────────────────────────────────────
if [[ $EUID -eq 0 ]]; then
    error "Do not run this script as root."
    exit 1
fi

cd "$SCRIPT_DIR"
echo ""
echo "REDLINE Installer"
echo "================="
echo "Directory: $SCRIPT_DIR"
echo ""

# ── Python version check ────────────────────────────────────────────────────
find_python() {
    for cmd in python3.12 python3.11 python3; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            local major=${ver%%.*}
            local minor=${ver##*.}
            if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python) || {
    error "Python $PYTHON_MIN+ is required but was not found."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install it with: brew install python@3.11"
    else
        echo "Install it with: sudo apt install python3.11  (Debian/Ubuntu)"
        echo "              or: sudo dnf install python3.11  (Fedora/RHEL)"
    fi
    exit 1
}

PYTHON_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
success "Python $PYTHON_VER ($PYTHON)"

# ── System packages (Linux only) ────────────────────────────────────────────
install_system_deps_linux() {
    if ! command -v apt-get &>/dev/null && ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        warn "No supported package manager found, skipping system package install."
        return
    fi

    info "Installing system packages..."

    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        local pkgs=(python3-dev build-essential libssl-dev libffi-dev)
        if [[ "$WEB_ONLY" == "false" ]]; then
            pkgs+=(python3-tk)
        fi
        sudo apt-get install -y "${pkgs[@]}" 2>/dev/null || warn "Some system packages failed to install."
    elif command -v dnf &>/dev/null || command -v yum &>/dev/null; then
        local pm; command -v dnf &>/dev/null && pm=dnf || pm=yum
        local pkgs=(python3-devel gcc gcc-c++ openssl-devel libffi-devel)
        if [[ "$WEB_ONLY" == "false" ]]; then
            pkgs+=(python3-tkinter)
        fi
        sudo "$pm" install -y "${pkgs[@]}" 2>/dev/null || warn "Some system packages failed to install."
    fi

    success "System packages done."
}

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if sudo -n true 2>/dev/null; then
        install_system_deps_linux
    else
        warn "No passwordless sudo; skipping system package install."
        warn "If the install fails, run: sudo apt install python3-dev build-essential python3-tk"
    fi
fi

# ── Virtual environment ──────────────────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/venv"

if [[ -d "$VENV_DIR" ]]; then
    info "Existing venv found at $VENV_DIR — reusing."
else
    info "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    success "Virtual environment created."
fi

# Activate
source "$VENV_DIR/bin/activate"

# ── pip upgrade ──────────────────────────────────────────────────────────────
info "Upgrading pip..."
pip install --quiet --upgrade pip setuptools wheel

# ── Install dependencies ─────────────────────────────────────────────────────
if [[ -f "requirements.txt" ]]; then
    info "Installing from requirements.txt..."
    pip install --quiet -r requirements.txt
    success "Python dependencies installed."
else
    error "requirements.txt not found. Are you running this from the project root?"
    exit 1
fi

# ── Install package (editable) ───────────────────────────────────────────────
if [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]]; then
    info "Installing REDLINE package (editable)..."
    pip install --quiet -e . 2>/dev/null || warn "Editable install failed — continuing without it."
fi

# ── Tkinter check ────────────────────────────────────────────────────────────
if [[ "$WEB_ONLY" == "false" ]]; then
    if python -c "import tkinter" 2>/dev/null; then
        success "Tkinter available (GUI supported)."
    else
        warn "Tkinter not available — GUI will not work. Use --web-only if you only need the web interface."
    fi
fi

# ── Data directories ─────────────────────────────────────────────────────────
info "Creating data directories..."
mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"
success "Directories: data/, logs/"

# ── .env setup ───────────────────────────────────────────────────────────────
if [[ "$SKIP_ENV" == "false" ]]; then
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        if [[ -f "$SCRIPT_DIR/env.template" ]]; then
            cp "$SCRIPT_DIR/env.template" "$SCRIPT_DIR/.env"
            success ".env created from env.template."
            warn "Edit .env and fill in your SECRET_KEY, Supabase, and Stripe credentials before starting."
        else
            warn "env.template not found — .env not created. Create it manually before starting."
        fi
    else
        info ".env already exists — skipping."
    fi
fi

# ── Verify core imports ───────────────────────────────────────────────────────
info "Verifying core imports..."
VERIFY_FAILED=false

python - <<'PYCHECK' || VERIFY_FAILED=true
import sys
checks = [
    ("flask",    "Flask"),
    ("pandas",   "pandas"),
    ("duckdb",   "DuckDB"),
    ("yfinance", "yfinance"),
]
failed = []
for mod, name in checks:
    try:
        __import__(mod)
    except ImportError:
        failed.append(name)

if failed:
    print(f"MISSING: {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
PYCHECK

if [[ "$VERIFY_FAILED" == "true" ]]; then
    error "Some core packages failed to import. Check the output above."
    exit 1
fi

success "Core imports OK."

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Installation complete."
echo "======================"
echo ""
echo "Start the web interface:"
echo "  source venv/bin/activate"
echo "  python web_app.py"
echo "  # or: gunicorn 'web_app:create_app()' --bind 0.0.0.0:8080"
echo ""
if [[ "$WEB_ONLY" == "false" ]]; then
echo "Start the desktop GUI:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
fi
echo "With Docker Compose:"
echo "  docker compose up"
echo ""
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    echo "Next step: edit .env with your credentials, then start the app."
fi
echo ""
