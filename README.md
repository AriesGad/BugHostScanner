# BugHost Scanner
A Python script for async subdomain scanning with HTTP and HTTPS support.


| __ ) _   _ | |   | | | ___
|  _ | | | / _| ' \ / __| | |/ _ \ | |) | || _ \ | | | (| | | () | |/ _,/|/| ||_|||___/ BugHost Scanner v3.1  |  Async + HTTPS + SNI

## Overview
BugHost Scanner is designed to enumerate subdomains for given domains using asynchronous requests. It supports HTTP and HTTPS with SNI, customizable wordlists, and output saving. Ideal for security researchers and pentesters.

## Installation
1. **Clone the Repository**:
   - On Termux, clone the repository:
     ```bash
     git clone https://github.com/Ariesgad/BugHostScanner.git
     cd BugHostScanner
     ```

2. **Set Up Dependencies**:
   - Run the installation script (adapted for Termux):
     ```bash
     chmod +x install.sh
     ./install.sh
     ```
   - Alternatively, install manually:
     ```bash
     pkg update -y && pkg upgrade -y
     pkg install -y git python python-pip
     pip install aiohttp tqdm colorama
     if [ ! -d "$HOME/storage/SecLists" ]; then git clone https://github.com/danielmiessler/SecLists.git "$HOME/storage/SecLists"; fi
     chmod +x bughost_scanner.py
     ```
   - Grant storage permission when prompted by `termux-setup-storage`.

## Usage
Run the scanner with Python (Termux doesn’t support the `bugscan` symlink easily):

### Basic Command
- Scan a single domain using the embedded default wordlist:
  ```bash
  python bughost_scanner.py -d example.com

 ## Target multiple domains with HTTPS:

  python bughost_scanner.py -d example.com,google.com --https


## Use SecLists (if cloned) and save results:

python bughost_scanner.py -d example.com -w $HOME/storage/SecLists/Discovery/DNS/subdomains-top1million-110000.txt -o results.txt
