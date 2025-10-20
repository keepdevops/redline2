#!/bin/bash
set -e

# Fix user creation issues for REDLINE installation

echo "🔧 Fixing REDLINE User Creation Issues"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

REDLINE_USER="redline"

echo "🔍 Current User Status:"
echo "======================"
echo "• Current user: $USER"
echo "• Current user ID: $(id -u)"
echo "• Current user groups: $(groups)"
echo "• REDLINE user exists: $(id "$REDLINE_USER" &>/dev/null && echo "Yes" || echo "No")"
echo ""

# Check if redline user exists
if id "$REDLINE_USER" &>/dev/null; then
    print_success "User $REDLINE_USER already exists"
    echo "• User ID: $(id -u "$REDLINE_USER")"
    echo "• Home directory: $(getent passwd "$REDLINE_USER" | cut -d: -f6)"
    echo "• Groups: $(groups "$REDLINE_USER")"
    exit 0
fi

print_status "User $REDLINE_USER does not exist. Creating..."

# Method 1: Try to create user normally
print_status "Method 1: Creating user with useradd..."
if sudo useradd -m -s /bin/bash $REDLINE_USER; then
    print_success "User $REDLINE_USER created successfully"
    
    # Add to docker group if it exists
    if getent group docker >/dev/null 2>&1; then
        sudo usermod -aG docker $REDLINE_USER
        print_success "User $REDLINE_USER added to docker group"
    else
        print_warning "Docker group not found, user not added to docker group"
    fi
    
    # Set a password for the user (optional)
    print_status "Setting password for $REDLINE_USER..."
    echo "$REDLINE_USER:$REDLINE_USER" | sudo chpasswd
    print_success "Password set for $REDLINE_USER"
    
    exit 0
fi

print_error "Failed to create user $REDLINE_USER with useradd"

# Method 2: Try alternative approach
print_status "Method 2: Trying alternative user creation..."
if sudo adduser --disabled-password --gecos "" $REDLINE_USER; then
    print_success "User $REDLINE_USER created with adduser"
    
    # Add to docker group if it exists
    if getent group docker >/dev/null 2>&1; then
        sudo usermod -aG docker $REDLINE_USER
        print_success "User $REDLINE_USER added to docker group"
    fi
    
    exit 0
fi

print_error "Failed to create user $REDLINE_USER with adduser"

# Method 3: Manual creation instructions
echo ""
print_warning "Automatic user creation failed. Here are manual steps:"
echo ""
echo "📋 Manual User Creation Steps:"
echo "=============================="
echo ""
echo "1. Create the user manually:"
echo "   sudo useradd -m -s /bin/bash $REDLINE_USER"
echo ""
echo "2. Set a password:"
echo "   sudo passwd $REDLINE_USER"
echo ""
echo "3. Add to docker group (if Docker is installed):"
echo "   sudo usermod -aG docker $REDLINE_USER"
echo ""
echo "4. Verify user creation:"
echo "   id $REDLINE_USER"
echo "   ls -la /home/$REDLINE_USER"
echo ""
echo "5. Then run the installation script again:"
echo "   ./install/install_ubuntu_intel.sh"
echo ""

# Alternative: Suggest current user installation
echo ""
print_status "Alternative: Install for current user instead"
echo "=================================================="
echo "If you prefer to install REDLINE for your current user ($USER):"
echo ""
echo "1. Use the current user installation script:"
echo "   ./install/install_ubuntu_intel_current_user.sh"
echo ""
echo "2. This will install REDLINE in your home directory:"
echo "   ~/redline/"
echo ""
echo "3. No additional user creation required"
echo ""

# Check system information
echo ""
echo "🔍 System Information:"
echo "====================="
echo "• Operating System: $(lsb_release -d | cut -f2)"
echo "• Architecture: $(uname -m)"
echo "• Current user: $USER"
echo "• User ID: $(id -u)"
echo "• Is root: $([ "$EUID" -eq 0 ] && echo "Yes" || echo "No")"
echo "• Sudo available: $(sudo -n true 2>/dev/null && echo "Yes" || echo "No")"
echo ""

print_status "Choose one of the options above to continue with REDLINE installation."
