#!/usr/bin/env python3
"""Minimal demo: start the OpenHear local WiFi endpoint.

Run with:
    python examples/openhear_wifi_demo.py

Then from another device on the same WiFi (or localhost):
    curl http://<this-machine>:8765/health
    curl http://<this-machine>:8765/haptic/profile/lewis
    curl -X POST http://<this-machine>:8765/haptic/event \\
         -H 'Content-Type: application/json' \\
         -d '{"event_type":"door_knock","facts":"Someone at the door","user_id":"lewis"}'
"""

from nexus_ai_hub import NexusHub, serve_openhear


def main() -> None:
    hub = NexusHub()
    # Bind to all interfaces so devices on the local WiFi (Starlink) can reach it.
    serve_openhear(hub, host="0.0.0.0", port=8765)


if __name__ == "__main__":
    main()
