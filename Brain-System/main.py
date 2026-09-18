#!/usr/bin/env python3
"""HRSploit Brain-System Gateway."""
import sys
from pathlib import Path
BASE = Path(__file__).parent
sys.path.insert(0, str(BASE.parent))

def run(target=None):
    from brain_orchestrator import BrainOrchestrator
    brain = BrainOrchestrator(target or "http://test.com")
    return brain.orchestrate()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Hedef: ").strip()
    decisions = run(target)
    for d in (decisions or []):
        print(f"  Karar: {d}")
