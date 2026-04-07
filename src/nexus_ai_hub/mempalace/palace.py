"""MemPalace core implementation for persistent memory storage and retrieval."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Memory:
    """A single memory entry in the MemPalace."""

    key: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class MemPalace:
    """Persistent memory store for the AI agent.

    MemPalace provides a simple key-value store with tagging and search
    capabilities, enabling long-term memory across conversations.

    Example::

        palace = MemPalace()
        palace.store("user_name", "Alice", tags=["profile"])
        memory = palace.recall("user_name")
    """

    def __init__(self) -> None:
        self._memories: dict[str, Memory] = {}

    def store(self, key: str, content: str, tags: list[str] | None = None) -> Memory:
        """Store or update a memory.

        Args:
            key: Unique identifier for the memory.
            content: The content to remember.
            tags: Optional tags for categorisation.

        Returns:
            The stored Memory object.
        """
        now = time.time()
        if key in self._memories:
            mem = self._memories[key]
            mem.content = content
            mem.tags = tags or mem.tags
            mem.updated_at = now
        else:
            mem = Memory(key=key, content=content, tags=tags or [], created_at=now, updated_at=now)
            self._memories[key] = mem
        return mem

    def recall(self, key: str) -> Memory | None:
        """Retrieve a memory by key.

        Args:
            key: The memory's unique identifier.

        Returns:
            The Memory object if found, otherwise None.
        """
        return self._memories.get(key)

    def search_by_tag(self, tag: str) -> list[Memory]:
        """Find all memories with a given tag.

        Args:
            tag: The tag to search for.

        Returns:
            A list of matching Memory objects.
        """
        return [m for m in self._memories.values() if tag in m.tags]

    def forget(self, key: str) -> bool:
        """Remove a memory by key.

        Args:
            key: The memory's unique identifier.

        Returns:
            True if the memory was removed, False if it was not found.
        """
        if key in self._memories:
            del self._memories[key]
            return True
        return False

    def list_keys(self) -> list[str]:
        """Return all stored memory keys."""
        return list(self._memories.keys())

    def export_json(self, path: str | Path) -> None:
        """Export all memories to a JSON file.

        Args:
            path: File path to write the JSON export.
        """
        data = {k: asdict(v) for k, v in self._memories.items()}
        Path(path).write_text(json.dumps(data, indent=2))

    def import_json(self, path: str | Path) -> int:
        """Import memories from a JSON file.

        Args:
            path: File path to read memories from.

        Returns:
            Number of memories imported.
        """
        data = json.loads(Path(path).read_text())
        count = 0
        for key, values in data.items():
            self._memories[key] = Memory(**values)
            count += 1
        return count
