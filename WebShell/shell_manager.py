#!/usr/bin/env python3
"""WebShell Manager — Generated shells are stored in tools/."""
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent / "tools"

def list_shells():
    return list(TOOLS_DIR.glob("*.php")) + list(TOOLS_DIR.glob("*.jsp")) + \
           list(TOOLS_DIR.glob("*.aspx")) + list(TOOLS_DIR.glob("*.py"))

def main():
    shells = list_shells()
    print(f"  Mevcut webshell'ler ({len(shells)}):")
    for s in shells:
        print(f"    - {s.name}")

if __name__ == "__main__":
    main()
