"""Renderer — process .il files through Jinja2 and write clean output."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from jinja2 import BaseLoader, Environment, TemplateNotFound

from infralight.core.decorators import IL_GLOBALS, begin_collect, end_collect
from infralight.core.models import FileKind, SourceFile, Visualization

log = logging.getLogger(__name__)

_BLANK_RUN = re.compile(r"\n{3,}")


class _StrLoader(BaseLoader):
    def __init__(self) -> None:
        self._t: dict[str, str] = {}

    def set(self, name: str, src: str) -> None:
        self._t[name] = src

    def get_source(self, env: Environment, template: str):
        if template not in self._t:
            raise TemplateNotFound(template)
        s = self._t[template]
        return s, template, lambda: True


def _make_env(loader: _StrLoader) -> Environment:
    env = Environment(loader=loader, keep_trailing_newline=True)
    env.globals.update(IL_GLOBALS)
    return env


def render_file(sf: SourceFile, output_dir: Path) -> tuple[str, Visualization]:
    """Render one file.  Returns (rendered_text, visualization)."""
    if sf.kind == FileKind.NATIVE:
        out = output_dir / sf.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(sf.content, encoding="utf-8")
        return sf.content, Visualization()

    loader = _StrLoader()
    loader.set(sf.name, sf.content)
    env = _make_env(loader)

    begin_collect(str(sf.path))
    try:
        rendered = env.get_template(sf.name).render()
    except Exception as exc:
        log.error("Render error %s: %s", sf.name, exc)
        return f"# RENDER ERROR: {exc}\n", Visualization()
    vis = end_collect()

    rendered = _BLANK_RUN.sub("\n\n", rendered).strip() + "\n"

    out = output_dir / sf.output_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    log.info("Rendered %s → %s", sf.name, out)
    return rendered, vis


def render_all(
    files: list[SourceFile], output_dir: Path
) -> tuple[dict[str, str], Visualization]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}
    combined = Visualization()
    for sf in files:
        txt, vis = render_file(sf, output_dir)
        results[sf.name] = txt
        combined.merge(vis)
    return results, combined


def extract_visualization(sf: SourceFile) -> Visualization:
    """Parse decorators without writing output (for live preview)."""
    if sf.kind == FileKind.NATIVE:
        return Visualization()
    loader = _StrLoader()
    loader.set(sf.name, sf.content)
    env = _make_env(loader)
    begin_collect(str(sf.path))
    try:
        env.get_template(sf.name).render()
    except Exception:
        return Visualization()
    return end_collect()
