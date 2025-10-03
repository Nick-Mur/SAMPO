"""Validate the advanced guide index structure against available topics.
Проверить структуру оглавления расширенного руководства и наличие тем."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ADVANCED_DIR = Path("docs/source/guidebook/advanced")


def extract_toctree_entries() -> list[str]:
    """Read the toctree section and return listed entries.
    Прочитать раздел toctree и вернуть перечисленные элементы."""

    content = ADVANCED_DIR.joinpath("index.md").read_text(encoding="utf-8")
    entries: list[str] = []
    capture = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```{toctree}"):
            capture = True
            continue
        if capture and stripped == "```":
            break
        if capture and stripped and not stripped.startswith(":") and not stripped.startswith("caption"):
            entries.append(stripped)
    return entries


def verify_entries(entries: list[str]) -> None:
    """Ensure every toctree entry has a corresponding documentation file.
    Убедиться, что у каждого элемента toctree есть соответствующий файл документации."""

    for entry in entries:
        doc_path = ADVANCED_DIR.joinpath(f"{entry}.md")
        exists = doc_path.exists()
        print(f"Entry '{entry}' -> {doc_path} exists: {exists}")


def main() -> None:
    """Extract and verify toctree entries from the advanced index.
    Извлечь и проверить элементы toctree из расширенного оглавления."""

    entries = extract_toctree_entries()
    print("Toctree entries:", entries)
    verify_entries(entries)


if __name__ == "__main__":
    main()
