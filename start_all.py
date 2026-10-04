#!/usr/bin/env python3
"""Unified service runner for TrialGuard / TechQuest.

Launches and monitors:
  1. Next.js Web Frontend       (Port 3000)
  2. FastAPI Ingress Gateway     (Port 8000)
  3. Compliance Specialist Agent (Port 8001)
  4. Safety Specialist Agent     (Port 8002)
  5. Financial Specialist Agent  (Port 8003)

Usage:
  python3 start_all.py            # Starts all 5 services
  python3 start_all.py --agents   # Starts only the 3 A2A microservices
  python3 start_all.py --gateway  # Starts only Gateway + Web
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# ANSI Colors
COLORS = {
    "WEB": "\033[96m",         # Cyan
    "GATEWAY": "\033[92m",     # Green
    "COMPLIANCE": "\033[93m",  # Yellow
    "SAFETY": "\033[91m",      # Red
    "FINANCIAL": "\033[95m",   # Magenta
    "SYSTEM": "\033[94m",      # Blue
    "RESET": "\033[0m",
}


SERVICES = [
    {
        "name": "COMPLIANCE",
        "port": 8001,
        "group": "agents",
        "cmd": ["uv", "run", "python", "apps/agent-compliance/server.py"],
        "cwd": REPO_ROOT,
    },
    {
        "name": "SAFETY",
        "port": 8002,
        "group": "agents",
        "cmd": ["uv", "run", "python", "apps/agent-safety/server.py"],
        "cwd": REPO_ROOT,
    },
    {
        "name": "FINANCIAL",
        "port": 8003,
        "group": "agents",
        "cmd": ["uv", "run", "python", "apps/agent-financial/server.py"],
        "cwd": REPO_ROOT,
    },
    {
        "name": "GATEWAY",
        "port": 8000,
        "group": "gateway",
        "cmd": ["uv", "run", "python", "apps/gateway/main.py"],
        "cwd": REPO_ROOT,
    },
    {
        "name": "WEB",
        "port": 3000,
        "group": "web",
        "cmd": ["pnpm", "--filter", "@techquest/web", "dev"],
        "cwd": REPO_ROOT,
    },
]

processes: list[subprocess.Popen] = []


def _stream_output(name: str, pipe) -> None:
    color = COLORS.get(name, "")
    reset = COLORS["RESET"]
    prefix = f"{color}[{name.ljust(10)}]{reset} "
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            sys.stdout.write(f"{prefix}{line}")
            sys.stdout.flush()
    except Exception:
        pass
    finally:
        pipe.close()


def shutdown(signum=None, frame=None) -> None:
    print(f"\n{COLORS['SYSTEM']}[SYSTEM] Shutting down all TrialGuard services...{COLORS['RESET']}")
    for proc in processes:
        if proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass

    for proc in processes:
        try:
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    print(f"{COLORS['SYSTEM']}[SYSTEM] All services stopped.{COLORS['RESET']}")
    sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start TrialGuard Services")
    parser.add_argument("--agents", action="store_true", help="Start only the 3 A2A specialist agents")
    parser.add_argument("--gateway", action="store_true", help="Start only Gateway and Web UI")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    active_services = []
    for s in SERVICES:
        if args.agents and s["group"] != "agents":
            continue
        if args.gateway and s["group"] not in ("gateway", "web"):
            continue
        active_services.append(s)

    print(f"{COLORS['SYSTEM']}==============================================================")
    print(f"  Starting TrialGuard Ecosystem ({len(active_services)} Services)")
    for s in active_services:
        print(f"    - {s['name'].ljust(12)} -> http://localhost:{s['port']}")
    print(f"=============================================================={COLORS['RESET']}\n")

    for s in active_services:
        try:
            proc = subprocess.Popen(
                s["cmd"],
                cwd=s["cwd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )
            processes.append(proc)
            t = threading.Thread(target=_stream_output, args=(s["name"], proc.stdout), daemon=True)
            t.start()
        except Exception as exc:
            print(f"{COLORS['SAFETY']}[ERROR] Failed to start {s['name']}: {exc}{COLORS['RESET']}")

    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
