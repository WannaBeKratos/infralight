"""Directory scanner — discovers .sls, .tf, .il.sls, .il.tf files."""

from __future__ import annotations

import logging
from pathlib import Path

from infralight.core.models import FileKind, FileType, Project, SourceFile

log = logging.getLogger(__name__)

_EXTENSION_MAP: list[tuple[str, FileType, FileKind]] = [
    (".il.sls", FileType.SALTSTACK, FileKind.IL),
    (".il.tf", FileType.TERRAFORM, FileKind.IL),
    (".sls", FileType.SALTSTACK, FileKind.NATIVE),
    (".tf", FileType.TERRAFORM, FileKind.NATIVE),
]

_SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".terraform",
    ".venv",
    "venv",
    "output",
}


def classify(path: Path) -> tuple[FileType, FileKind] | None:
    name = path.name.lower()
    for ext, ft, fk in _EXTENSION_MAP:
        if name.endswith(ext):
            return ft, fk
    return None


def scan_directory(root: Path) -> Project:
    """Recursively scan *root* and return a populated Project."""
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Not a directory: {root}")

    project = Project(root=root, output_dir=root / "output")

    for path in sorted(root.rglob("*")):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        result = classify(path)
        if result is None:
            continue

        ft, fk = result
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            log.warning("Could not read %s", path)
            continue

        project.files.append(
            SourceFile(path=path, file_type=ft, kind=fk, content=content)
        )

    log.info("Scanned %s — %d files", root, len(project.files))
    return project
