"""Tests for the MemPalace module."""

import json
from pathlib import Path

from nexus_ai_hub.mempalace.palace import Memory, MemPalace


class TestMemory:
    def test_creation(self) -> None:
        mem = Memory(key="k", content="v")
        assert mem.key == "k"
        assert mem.content == "v"
        assert mem.tags == []

    def test_creation_with_tags(self) -> None:
        mem = Memory(key="k", content="v", tags=["a", "b"])
        assert mem.tags == ["a", "b"]


class TestMemPalace:
    def test_store_and_recall(self) -> None:
        palace = MemPalace()
        palace.store("name", "Alice")
        mem = palace.recall("name")
        assert mem is not None
        assert mem.content == "Alice"

    def test_recall_missing_key(self) -> None:
        palace = MemPalace()
        assert palace.recall("nonexistent") is None

    def test_store_with_tags(self) -> None:
        palace = MemPalace()
        palace.store("color", "blue", tags=["pref", "visual"])
        mem = palace.recall("color")
        assert mem is not None
        assert "pref" in mem.tags

    def test_update_existing_memory(self) -> None:
        palace = MemPalace()
        palace.store("key", "old")
        palace.store("key", "new")
        mem = palace.recall("key")
        assert mem is not None
        assert mem.content == "new"

    def test_search_by_tag(self) -> None:
        palace = MemPalace()
        palace.store("a", "1", tags=["x"])
        palace.store("b", "2", tags=["x", "y"])
        palace.store("c", "3", tags=["y"])
        results = palace.search_by_tag("x")
        assert len(results) == 2

    def test_forget(self) -> None:
        palace = MemPalace()
        palace.store("temp", "data")
        assert palace.forget("temp") is True
        assert palace.recall("temp") is None

    def test_forget_missing(self) -> None:
        palace = MemPalace()
        assert palace.forget("missing") is False

    def test_list_keys(self) -> None:
        palace = MemPalace()
        palace.store("a", "1")
        palace.store("b", "2")
        keys = palace.list_keys()
        assert set(keys) == {"a", "b"}

    def test_export_and_import_json(self, tmp_path: Path) -> None:
        palace = MemPalace()
        palace.store("name", "Bob", tags=["profile"])
        export_path = tmp_path / "memories.json"
        palace.export_json(export_path)

        # Verify the JSON file
        data = json.loads(export_path.read_text())
        assert "name" in data
        assert data["name"]["content"] == "Bob"

        # Import into a new palace
        new_palace = MemPalace()
        count = new_palace.import_json(export_path)
        assert count == 1
        mem = new_palace.recall("name")
        assert mem is not None
        assert mem.content == "Bob"
