#!/usr/bin/env python3
import aiohttp
import asyncio
import socket
import argparse
import os
from tqdm import tqdm
from colorama import Fore, Style, init

# Check for required dependencies
try:
    init(autoreset=True)
except NameError:
    print("❌ Error: 'colorama' module not found. Install it with 'pip install colorama'")
    exit(1)

# Embedded default wordlist (small fallback)
DEFAULT_WORDLIST = [
    "www",
    "mail",
    "ftp",
    "api",
    "dev",
    "test",
    "staging",
    "blog",
    "shop",
    "forum",
]

BANNER = f"""{Fore.CYAN}
 ____            _          _ _       
| __ ) _   _ ___| |__   ___| | | ___  
|  _ \| | | / __| '_ \ / __| | |/ _ \ 
| |_) | |_| \__ \ | | | (__| | | (_) |
|____/ \__,_/|___/_| |_|____|_|_|\___/
        BugHost Scanner v3.1  |  Async + HTTPS + SNI
{Style.RESET_ALL}"""

async def fetch(session, url, host):
    try:
        async with session.get(url, timeout=5, allow_redirects=True, ssl=False) as response:
            if response.status < 400:
                server = response.headers.get("Server", "Unknown")
                location = response.headers.get("Location", "None")
                result = f"{Fore.GREEN}[+] {host} [{response.status}] | Server: {server} | Redirect: {location}"
                print(result)
                return result
    except Exception:
        return None

async def scan(domains, wordlist, output, concurrency, https):
    found = []
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        # Load wordlist
        subs = []
        if wordlist:
            try:
                with open(wordlist, "r", errors="ignore") as file:
                    subs = [line.strip() for line in file if line.strip()]
                print(f"📋 Using wordlist: {wordlist}")
            except FileNotFoundError:
                print(f"❌ Error: Wordlist file '{wordlist}' not found")
                wordlist = None

        # Fallback to sample wordlist or embedded wordlist
        if not wordlist or not subs:
            sample_wordlist = os.path.join(os.path.dirname(__file__), "wordlists", "wordlist.txt")
            seclists_path = os.path.expanduser("~/SecLists/Discovery/DNS/subdomains-top1million-110000.txt")
            
            if wordlist == seclists_path and not os.path.exists(seclists_path):
                print(f"❌ SecLists not found at {seclists_path}")
            elif os.path.exists(sample_wordlist):
                try:
                    with open(sample_wordlist, "r", errors="ignore") as file:
                        subs = [line.strip() for line in file if line.strip()]
                    print(f"📋 Using sample wordlist: {sample_wordlist}")
                except FileNotFoundError:
                    pass
            
            if not subs:
                print("📋 Falling back to embedded default wordlist")
                subs = DEFAULT_WORDLIST

        for domain in domains:
            for sub in subs:
                host = f"{sub}.{domain}"
                try:
                    socket.gethostbyname(host)
                    url = f"https://{host}" if https else f"http://{host}"
                    tasks.append(fetch(session, url, host))
                except socket.gaierror:
                    pass  # Skip invalid hosts

        for ftask in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scanning", unit="host"):
            result = await ftask
            if result:
                found.append(result)

    if output and found:
        with open(output, "w") as out_file:
            for host in found:
                clean = host.replace(Fore.GREEN, "").replace(Style.RESET_ALL, "")
                out_file.write(clean + "\n")
        print(f"\n✅ Saved {len(found)} hosts to {output}")
    elif not found:
        print("\n⚠️ No valid hosts found")

if __name__ == "__main__":
    print(BANNER)
    parser = argparse.ArgumentParser(description="Async Bug Host Scanner")
    parser.add_argument("-d", "--domain", required=True, help="Comma-separated domains (e.g., example.com,domain.com)")
    parser.add_argument("-w", "--wordlist", default="", help="Subdomain wordlist (default: SecLists or sample wordlist)")
    parser.add_argument("-o", "--output", default="found.txt", help="Output file for results")
    parser.add_argument("-c", "--concurrency", type=int, default=100, help="Number of concurrent requests")
    parser.add_argument("--https", action="store_true", help="Use HTTPS with SNI (default: HTTP)")
    args = parser.parse_args()

    # Validate domains
    domains = [d.strip() for d in args.domain.split(",") if d.strip()]
    if not domains:
        print("❌ Error: No valid domains provided")
        exit(1)

    # Set default wordlist path
    wordlist = args.wordlist
    if not wordlist:
        seclists_path = os.path.expanduser("~/SecLists/Discovery/DNS/subdomains-top1million-110000.txt")
        sample_wordlist = os.path.join(os.path.dirname(__file__), "wordlists", "wordlist.txt")
        
        if os.path.exists(seclists_path):
            wordlist = seclists_path
            print(f"📂 Using SecLists: {wordlist}")
        elif os.path.exists(sample_wordlist):
            wordlist = sample_wordlist
            print(f"📋 Using sample wordlist: {sample_wordlist}")
        else:
            print(f"📋 SecLists not found at {seclists_path}, falling back to embedded wordlist")
            wordlist = None

    # Validate wordlist file if provided
    if wordlist and not os.path.exists(wordlist):
        print(f"❌ Error: Wordlist file '{wordlist}' does not exist, checking fallbacks")
        wordlist = None

    # Run the scanner
    asyncio.run(scan(domains, wordlist, args.output, args.concurrency, args.https))
