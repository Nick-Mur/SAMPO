"""Validate the advanced guide index. Проверить индекс раздела advanced."""

from __future__ import annotations

from pathlib import Path


def extract_toctree_entries(index_path: Path) -> list[str]:
    """Parse toctree entries from the index file. Извлечь элементы toctree из файла индекса."""
    entries: list[str] = []
    inside = False
    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("```{toctree}"):
            inside = True
            continue
        if not inside:
            continue
        if line == "```":
            break
        if not line or ":" in line:
            continue
        entries.append(line)
    return entries


def validate_entries() -> None:
    """Ensure index references every documentation page. Убедиться, что индекс ссылается на все страницы."""
    advanced_dir = Path(__file__).resolve().parents[1]
    index_path = advanced_dir / "index.md"
    assert index_path.exists(), "index.md is missing"
    entries = extract_toctree_entries(index_path)
    assert entries, "No entries parsed from index.md"
    for entry in entries:
        target = advanced_dir / f"{entry}.md"
        assert target.exists(), f"Missing documentation file for {entry}"


def main() -> None:
    """Run index validation. Выполнить проверку индекса."""
    validate_entries()


if __name__ == "__main__":
    main()
