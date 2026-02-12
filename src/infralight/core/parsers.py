"""Parsers — extract IaCResource entries from SaltStack and Terraform files."""

from __future__ import annotations

import logging
import re
from typing import Any

import yaml

from infralight.core.models import FileType, IaCResource, SourceFile

log = logging.getLogger(__name__)
# Salt requisite keywords — these define dependencies between states
_SALT_REQUISITES = frozenset(
    {
        "require",
        "require_in",
        "watch",
        "watch_in",
        "onchanges",
        "onchanges_in",
        "onfail",
        "onfail_in",
        "prereq",
        "prereq_in",
        "use",
        "use_in",
        "listen",
        "listen_in",
    }
)


def _extract_requisites(
    params: list[Any] | dict[str, Any],
) -> list[dict[str, str]]:
    """Pull requisite entries from Salt state params.

    Returns a list of ``{"type": <requisite_kind>, "module": <mod>, "state": <id>}``.
    """
    reqs: list[dict[str, str]] = []
    items: list[Any] = params if isinstance(params, list) else [params]
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in _SALT_REQUISITES:
            if key not in item:
                continue
            val = item[key]
            if isinstance(val, list):
                for entry in val:
                    if isinstance(entry, dict):
                        for mod, sid in entry.items():
                            reqs.append(
                                {"type": key, "module": str(mod), "state": str(sid)}
                            )
                    elif isinstance(entry, str):
                        reqs.append({"type": key, "module": "_", "state": entry})
    return reqs


def parse_salt(sf: SourceFile) -> list[IaCResource]:
    """Parse a SaltStack .sls file into IaCResource entries.

    SaltStack states have the form::

        <state_id>:
          <module>.<function>:
            - name: ...
            - key: val

    Requisites (``require``, ``watch``, etc.) are extracted into
    ``properties["__requisites"]``.
    """
    resources: list[IaCResource] = []
    try:
        data = yaml.safe_load(sf.content)
    except Exception as exc:
        log.warning("YAML parse error in %s: %s", sf.name, exc)
        return resources

    if not isinstance(data, dict):
        return resources

    # Track line numbers — walk raw lines to map state IDs
    line_map: dict[str, int] = {}
    for lineno, line in enumerate(sf.content.splitlines(), 1):
        stripped = line.rstrip()
        if stripped and not stripped[0].isspace() and stripped.endswith(":"):
            line_map[stripped[:-1]] = lineno

    for state_id, body in data.items():
        if not isinstance(body, dict):
            continue
        for mod_func, params in body.items():
            if not isinstance(mod_func, str) or "." not in mod_func:
                continue
            props: dict[str, Any] = {}
            if isinstance(params, list):
                for item in params:
                    if isinstance(item, dict):
                        props.update(item)
            elif isinstance(params, dict):
                props = dict(params)

            # Extract requisites into a separate key
            reqs = _extract_requisites(
                params if isinstance(params, (list, dict)) else []
            )
            if reqs:
                props["__requisites"] = reqs

            # Determine module category
            module = mod_func.split(".")[0] if "." in mod_func else mod_func
            props["__module"] = module
            props["__function"] = mod_func.split(".", 1)[1] if "." in mod_func else ""

            resources.append(
                IaCResource(
                    id=state_id,
                    name=props.get("name", state_id),
                    resource_type=mod_func,
                    provider="salt",
                    source_file=str(sf.path),
                    source_line=line_map.get(state_id, 0),
                    properties=props,
                )
            )

    return resources


_TF_RESOURCE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_DATA = re.compile(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_VARIABLE = re.compile(r'variable\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_OUTPUT = re.compile(r'output\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_PROVIDER = re.compile(r'provider\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_MODULE = re.compile(r'module\s+"([^"]+)"\s*\{', re.MULTILINE)
_TF_ATTR = re.compile(r'^\s+(\w+)\s*=\s*"?([^"\n]*)"?', re.MULTILINE)


def _extract_block_attrs(text: str, start: int) -> dict[str, str]:
    """Extract shallow key = value pairs from a block."""
    depth = 0
    attrs: dict[str, str] = {}
    i = text.index("{", start)
    block_start = i
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                block_text = text[block_start + 1 : j]
                for m in _TF_ATTR.finditer(block_text):
                    # only top-level attrs (not nested blocks)
                    attrs[m.group(1)] = m.group(2).strip()
                break
    return attrs


def parse_terraform(sf: SourceFile) -> list[IaCResource]:
    """Parse a Terraform .tf file into IaCResource entries."""
    resources: list[IaCResource] = []
    text = sf.content

    for m in _TF_RESOURCE.finditer(text):
        rtype, rname = m.group(1), m.group(2)
        attrs = _extract_block_attrs(text, m.start())
        provider = rtype.split("_")[0] if "_" in rtype else rtype
        resources.append(
            IaCResource(
                id=f"{rtype}.{rname}",
                name=rname,
                resource_type=rtype,
                provider=provider,
                source_file=str(sf.path),
                source_line=text[: m.start()].count("\n") + 1,
                properties=attrs,
            )
        )

    for m in _TF_DATA.finditer(text):
        dtype, dname = m.group(1), m.group(2)
        attrs = _extract_block_attrs(text, m.start())
        resources.append(
            IaCResource(
                id=f"data.{dtype}.{dname}",
                name=dname,
                resource_type=f"data.{dtype}",
                provider=dtype.split("_")[0] if "_" in dtype else dtype,
                source_file=str(sf.path),
                source_line=text[: m.start()].count("\n") + 1,
                properties=attrs,
            )
        )

    for m in _TF_VARIABLE.finditer(text):
        vname = m.group(1)
        attrs = _extract_block_attrs(text, m.start())
        resources.append(
            IaCResource(
                id=f"var.{vname}",
                name=vname,
                resource_type="variable",
                provider="terraform",
                source_file=str(sf.path),
                source_line=text[: m.start()].count("\n") + 1,
                properties=attrs,
            )
        )

    for m in _TF_OUTPUT.finditer(text):
        oname = m.group(1)
        attrs = _extract_block_attrs(text, m.start())
        resources.append(
            IaCResource(
                id=f"output.{oname}",
                name=oname,
                resource_type="output",
                provider="terraform",
                source_file=str(sf.path),
                source_line=text[: m.start()].count("\n") + 1,
                properties=attrs,
            )
        )

    for m in _TF_MODULE.finditer(text):
        mname = m.group(1)
        attrs = _extract_block_attrs(text, m.start())
        resources.append(
            IaCResource(
                id=f"module.{mname}",
                name=mname,
                resource_type="module",
                provider="terraform",
                source_file=str(sf.path),
                source_line=text[: m.start()].count("\n") + 1,
                properties=attrs,
            )
        )

    return resources


def parse_file(sf: SourceFile) -> list[IaCResource]:
    if sf.file_type == FileType.SALTSTACK:
        return parse_salt(sf)
    return parse_terraform(sf)
