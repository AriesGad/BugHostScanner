#!/data/data/com.termux/files/usr/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "[*] ${GREEN}Installing BugHost Scanner on Termux...${NC}"

# Update and install dependencies
pkg update -y && pkg upgrade -y || { echo -e "${RED}❌ Error: pkg update/upgrade failed${NC}"; exit 1; }
pkg install -y git python python-pip || { echo -e "${RED}❌ Error: pkg install failed${NC}"; exit 1; }

# Install Python dependencies
pip install aiohttp tqdm colorama || { echo -e "${RED}❌ Error: pip install failed${NC}"; exit 1; }

# Set up storage (required for SecLists)
if [ ! -d "$HOME/storage" ]; then
    termux-setup-storage || { echo -e "${RED}❌ Error: Storage setup failed. Grant storage permission${NC}"; exit 1; }
fi

# Clone SecLists if missing
SECLISTS_DIR="$HOME/storage/SecLists"
if [ ! -d "$SECLISTS_DIR" ]; then
    echo -e "[*] ${GREEN}Cloning SecLists to $SECLISTS_DIR...${NC}"
    git clone https://github.com/danielmiessler/SecLists.git "$SECLISTS_DIR" || { echo -e "${RED}❌ Error: SecLists clone failed${NC}"; exit 1; }
else
    echo -e "[*] ${GREEN}SecLists already exists at $SECLISTS_DIR${NC}"
fi

# Check if bughost_scanner.py exists
if [ -f "$(pwd)/bughost_scanner.py" ]; then
    chmod +x "$(pwd)/bughost_scanner.py" || { echo -e "${RED}❌ Error: Failed to set execute permissions${NC}"; exit 1; }
    
    # Termux doesn't support /usr/local/bin symlink easily; use a local alias instead
    echo -e "${GREEN}✅ Script is executable. Run: python $(pwd)/bughost_scanner.py -d example.com,google.com${NC}"
else
    echo -e "${RED}❌ Error: bughost_scanner.py not found in current directory${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Installation complete on Termux!${NC}"
