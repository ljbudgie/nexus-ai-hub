"""Local WiFi-accessible endpoint for OpenHear haptic and perceptual events.

Minimal stdlib HTTP server so OpenHear hardware (or a phone proxy) can talk
to the Nexus hub over local WiFi (e.g. Starlink) without external dependencies.

All actions go through the Burgess gate. Approved events are stored in MemPalace
as sensory records.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from nexus_ai_hub.core import NexusHub


class OpenHearHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OpenHear local API."""

    hub: NexusHub  # set on the class before serving

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/haptic/profile/"):
            user_id = parsed.path.split("/")[-1]
            profile = self.hub.openhear.get_haptic_profile(user_id)
            self._send_json(
                200,
                {
                    "user_id": profile.user_id,
                    "pattern_id": profile.pattern_id,
                    "channels": list(profile.channels),
                    "rhythm": profile.rhythm,
                    "duration_ms": profile.duration_ms,
                    "intensity": profile.intensity,
                    "semantic_label": profile.semantic_label,
                },
            )
            return
        if parsed.path == "/health":
            self._send_json(200, {"status": "ok", "component": "openhear-local"})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        if parsed.path == "/haptic/event":
            event_type = payload.get("event_type", "unknown")
            facts = payload.get("facts", f"Haptic event: {event_type}")
            user_id = payload.get("user_id", "local")
            action = f"emit_haptic_{event_type}"

            from nexus_ai_hub.core import BurgessContext

            ctx = BurgessContext(
                domain="sensory",
                facts=facts,
                metadata={"user_id": user_id, "event_type": event_type, "impact_class": "low"},
            )
            record = self.hub.review(action, ctx)

            response: dict[str, Any] = {
                "action": action,
                "decision": record.decision.value if hasattr(record.decision, "value") else str(record.decision),
                "allowed": self.hub.is_allowed(record),
                "rationale": record.rationale,
                "ledger_index": record.index,
            }

            if self.hub.is_allowed(record):
                # Store in MemPalace as a sensory memory
                key = f"haptic_event_{record.index}"
                self.hub.mempalace.store_sensory(
                    key=key,
                    content=facts,
                    tags=[event_type, "wifi"],
                )
                response["stored"] = True
                response["memory_key"] = key
            else:
                response["stored"] = False
                response["note"] = "Blocked pending human review (Burgess NULL)"

            self._send_json(200, response)
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Quiet by default; override if you want request logging
        pass


def serve_openhear(hub: NexusHub, host: str = "0.0.0.0", port: int = 8765) -> None:
    """Start the local OpenHear WiFi endpoint.

    Args:
        hub: A configured NexusHub instance.
        host: Bind address. Use 0.0.0.0 to accept connections from devices on the local WiFi.
        port: Port to listen on.
    """
    OpenHearHandler.hub = hub
    server = HTTPServer((host, port), OpenHearHandler)
    print(f"OpenHear local endpoint listening on http://{host}:{port}")
    print("  GET  /health")
    print("  GET  /haptic/profile/<user_id>")
    print("  POST /haptic/event   {\"event_type\": \"door_knock\", \"facts\": \"...\"}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
