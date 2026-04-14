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

    def test_timestamps_are_set(self) -> None:
        mem = Memory(key="k", content="v")
        assert isinstance(mem.created_at, float)
        assert isinstance(mem.updated_at, float)
        assert mem.created_at > 0
        assert mem.updated_at > 0

    def test_custom_timestamps(self) -> None:
        mem = Memory(key="k", content="v", created_at=1.0, updated_at=2.0)
        assert mem.created_at == 1.0
        assert mem.updated_at == 2.0

    def test_tags_default_factory_isolation(self) -> None:
        """Each Memory instance should get its own tags list."""
        mem1 = Memory(key="a", content="1")
        mem2 = Memory(key="b", content="2")
        mem1.tags.append("x")
        assert "x" not in mem2.tags

    def test_empty_content(self) -> None:
        mem = Memory(key="k", content="")
        assert mem.content == ""

    def test_special_characters_in_key_and_content(self) -> None:
        mem = Memory(key="key/with:special chars!", content="émojis 🧠")
        assert mem.key == "key/with:special chars!"
        assert mem.content == "émojis 🧠"


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

    def test_len(self) -> None:
        palace = MemPalace()
        assert len(palace) == 0
        palace.store("a", "1")
        assert len(palace) == 1
        palace.store("b", "2")
        assert len(palace) == 2
        palace.forget("a")
        assert len(palace) == 1

    def test_contains(self) -> None:
        palace = MemPalace()
        palace.store("name", "Alice")
        assert "name" in palace
        assert "missing" not in palace

    def test_repr(self) -> None:
        palace = MemPalace()
        assert "MemPalace" in repr(palace)
        assert "memories=0" in repr(palace)
        palace.store("a", "1")
        assert "memories=1" in repr(palace)

    # ----- New edge-case and behavioral tests -----

    def test_store_returns_memory(self) -> None:
        palace = MemPalace()
        mem = palace.store("k", "v", tags=["t"])
        assert isinstance(mem, Memory)
        assert mem.key == "k"
        assert mem.content == "v"
        assert mem.tags == ["t"]

    def test_update_preserves_created_at(self) -> None:
        """Updating a memory should keep created_at but update updated_at."""
        palace = MemPalace()
        mem1 = palace.store("k", "old")
        created = mem1.created_at
        # Store again to trigger update
        mem2 = palace.store("k", "new")
        assert mem2.created_at == created
        assert mem2.updated_at >= mem1.updated_at

    def test_update_without_tags_preserves_tags(self) -> None:
        """Updating without specifying tags should preserve existing tags."""
        palace = MemPalace()
        palace.store("k", "v", tags=["original"])
        palace.store("k", "v2")  # no tags specified
        mem = palace.recall("k")
        assert mem is not None
        assert mem.tags == ["original"]

    def test_update_with_tags_replaces_tags(self) -> None:
        """Updating with new tags should replace existing tags."""
        palace = MemPalace()
        palace.store("k", "v", tags=["old"])
        palace.store("k", "v2", tags=["new"])
        mem = palace.recall("k")
        assert mem is not None
        assert mem.tags == ["new"]

    def test_search_by_tag_no_matches(self) -> None:
        palace = MemPalace()
        palace.store("a", "1", tags=["x"])
        assert palace.search_by_tag("nonexistent") == []

    def test_search_by_tag_empty_palace(self) -> None:
        palace = MemPalace()
        assert palace.search_by_tag("any") == []

    def test_list_keys_empty(self) -> None:
        palace = MemPalace()
        assert palace.list_keys() == []

    def test_list_keys_after_forget(self) -> None:
        palace = MemPalace()
        palace.store("a", "1")
        palace.store("b", "2")
        palace.forget("a")
        assert palace.list_keys() == ["b"]

    def test_export_empty_palace(self, tmp_path: Path) -> None:
        palace = MemPalace()
        path = tmp_path / "empty.json"
        palace.export_json(path)
        data = json.loads(path.read_text())
        assert data == {}

    def test_export_import_multiple_memories(self, tmp_path: Path) -> None:
        palace = MemPalace()
        palace.store("a", "1", tags=["x"])
        palace.store("b", "2", tags=["y"])
        palace.store("c", "3", tags=["x", "y"])
        path = tmp_path / "multi.json"
        palace.export_json(path)

        new_palace = MemPalace()
        count = new_palace.import_json(path)
        assert count == 3
        assert len(new_palace) == 3
        assert new_palace.recall("a") is not None
        assert new_palace.recall("b") is not None
        assert new_palace.recall("c") is not None

    def test_import_preserves_tags(self, tmp_path: Path) -> None:
        palace = MemPalace()
        palace.store("k", "v", tags=["tag1", "tag2"])
        path = tmp_path / "tags.json"
        palace.export_json(path)

        new_palace = MemPalace()
        new_palace.import_json(path)
        mem = new_palace.recall("k")
        assert mem is not None
        assert mem.tags == ["tag1", "tag2"]

    def test_import_preserves_timestamps(self, tmp_path: Path) -> None:
        palace = MemPalace()
        stored = palace.store("k", "v")
        path = tmp_path / "ts.json"
        palace.export_json(path)

        new_palace = MemPalace()
        new_palace.import_json(path)
        mem = new_palace.recall("k")
        assert mem is not None
        assert mem.created_at == stored.created_at
        assert mem.updated_at == stored.updated_at

    def test_export_json_with_string_path(self, tmp_path: Path) -> None:
        palace = MemPalace()
        palace.store("k", "v")
        path = str(tmp_path / "str_path.json")
        palace.export_json(path)
        data = json.loads(Path(path).read_text())
        assert "k" in data

    def test_import_json_with_string_path(self, tmp_path: Path) -> None:
        palace = MemPalace()
        palace.store("k", "v")
        path = str(tmp_path / "str_import.json")
        palace.export_json(path)

        new_palace = MemPalace()
        count = new_palace.import_json(path)
        assert count == 1

    def test_contains_non_string_key(self) -> None:
        """The __contains__ signature accepts object; non-string should not raise."""
        palace = MemPalace()
        palace.store("k", "v")
        assert 42 not in palace  # type: ignore[operator]
        assert None not in palace  # type: ignore[operator]

    def test_forget_after_forget(self) -> None:
        """Forgetting the same key twice should return False the second time."""
        palace = MemPalace()
        palace.store("k", "v")
        assert palace.forget("k") is True
        assert palace.forget("k") is False

    def test_store_empty_content(self) -> None:
        palace = MemPalace()
        mem = palace.store("k", "")
        assert mem.content == ""

    def test_full_lifecycle(self) -> None:
        """Store → update → search → forget → verify gone."""
        palace = MemPalace()
        palace.store("user", "Alice", tags=["profile"])
        assert "user" in palace
        assert palace.recall("user") is not None

        palace.store("user", "Bob", tags=["profile", "updated"])
        mem = palace.recall("user")
        assert mem is not None
        assert mem.content == "Bob"
        assert "updated" in mem.tags

        results = palace.search_by_tag("profile")
        assert len(results) == 1

        assert palace.forget("user") is True
        assert palace.recall("user") is None
        assert "user" not in palace
        assert len(palace) == 0
