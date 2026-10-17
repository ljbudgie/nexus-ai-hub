"""nexus — one-command first-time experience for the local OpenHear/Iris hub."""

from __future__ import annotations

import argparse
import sys

from nexus_ai_hub import IrisCompanion, NexusHub, serve_openhear


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nexus AI Hub — local-first OpenHear + Iris companion",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    args = parser.parse_args()

    hub = NexusHub()
    iris = IrisCompanion(hub)

    print()
    print("Nexus AI Hub")
    print("============")
    print("Local-first OpenHear + Iris companion")
    print("Burgess Principle enforced on every action")
    print()
    print(f"Listening on http://{args.host}:{args.port}")
    print()
    print("Try it from another device on the same WiFi:")
    print(f"  curl http://localhost:{args.port}/health")
    print(f"  curl http://localhost:{args.port}/haptic/profile/you")
    print()
    print("  curl -X POST http://localhost:{args.port}/haptic/event \\")
    print("       -H 'Content-Type: application/json' \\")
    print('       -d \'{"event_type":"door_knock","facts":"Someone at the door"}\'')
    print()
    print("Pure notifications (door knock, traffic…) are low-impact → SOVEREIGN.")
    print("Anything higher-stakes still requires a named human review.")
    print()
    print("Press Ctrl+C to stop.")
    print()

    # Quiet smoke-test so the first-time user sees Iris working immediately
    surface = iris.on_haptic_event("door_knock", "Someone at the door", user_id="you")
    print(f"Iris ready: {surface.message}")
    print()

    try:
        serve_openhear(hub, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nStopped. Memory and ledger stay on disk.")
        sys.exit(0)


if __name__ == "__main__":
    main()
