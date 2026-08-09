#!/usr/bin/env python3
# Vibe coded by Codex
"""List the file formats registered by the locally installed GIMP."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True)
class FileHandler:
    action: str
    label: str
    extensions: tuple[str, ...]
    mime_types: tuple[str, ...]
    procedure: str
    plugin: str
    priority: str
    flags: tuple[str, ...]


class RegistryError(RuntimeError):
    """Raised when GIMP's plug-in registry cannot be read."""


def tokenize_sexpressions(source: str) -> Iterator[str]:
    """Tokenize the small S-expression dialect used by GIMP's pluginrc."""
    index = 0
    length = len(source)

    while index < length:
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char == "#":
            newline = source.find("\n", index)
            index = length if newline < 0 else newline + 1
            continue
        if char in "()":
            yield char
            index += 1
            continue
        if char == '"':
            index += 1
            value: list[str] = []
            while index < length:
                char = source[index]
                if char == '"':
                    index += 1
                    break
                if char != "\\":
                    value.append(char)
                    index += 1
                    continue

                index += 1
                if index >= length:
                    raise RegistryError("unterminated escape in pluginrc string")
                escaped = source[index]
                if escaped in "01234567":
                    end = index + 1
                    while end < min(index + 3, length) and source[end] in "01234567":
                        end += 1
                    value.append(chr(int(source[index:end], 8)))
                    index = end
                    continue
                value.append({"n": "\n", "r": "\r", "t": "\t"}.get(escaped, escaped))
                index += 1
            else:
                raise RegistryError("unterminated quoted string in pluginrc")
            yield "".join(value)
            continue

        end = index
        while end < length and not source[end].isspace() and source[end] not in "()#":
            end += 1
        yield source[index:end]
        index = end


def parse_sexpressions(source: str) -> list[object]:
    """Parse pluginrc into nested Python lists while preserving atom text."""
    root: list[object] = []
    stack: list[list[object]] = [root]

    for token in tokenize_sexpressions(source):
        if token == "(":
            expression: list[object] = []
            stack[-1].append(expression)
            stack.append(expression)
        elif token == ")":
            if len(stack) == 1:
                raise RegistryError("unexpected ')' in pluginrc")
            stack.pop()
        else:
            stack[-1].append(token)

    if len(stack) != 1:
        raise RegistryError("unterminated expression in pluginrc")
    return root


def is_form(value: object, name: str) -> bool:
    return isinstance(value, list) and bool(value) and value[0] == name


def direct_form(expression: Sequence[object], *names: str) -> list[object] | None:
    for value in expression:
        if isinstance(value, list) and value and value[0] in names:
            return value
    return None


def form_value(expression: Sequence[object], name: str, default: str = "") -> str:
    value = direct_form(expression, name)
    if value is None or len(value) < 2 or not isinstance(value[1], str):
        return default
    return value[1]


def comma_values(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def clean_label(label: str, blurb: str, procedure: str) -> str:
    chosen = label or blurb or procedure
    chosen = chosen.replace("_", "").strip()
    return re.sub(r"\.{3}$", "", chosen)


def parse_registry(path: Path) -> list[FileHandler]:
    try:
        source = path.read_text(encoding="utf-8", errors="surrogateescape")
    except OSError as error:
        raise RegistryError(f"cannot read {path}: {error}") from error

    handlers: list[FileHandler] = []
    for plugin_definition in parse_sexpressions(source):
        if not is_form(plugin_definition, "plug-in-def"):
            continue
        assert isinstance(plugin_definition, list)
        plugin_path = str(plugin_definition[1]) if len(plugin_definition) > 1 else "unknown"
        plugin_name = Path(plugin_path).name

        for procedure_definition in plugin_definition:
            if not is_form(procedure_definition, "proc-def"):
                continue
            assert isinstance(procedure_definition, list)
            handler_form = direct_form(procedure_definition, "load-proc", "save-proc")
            if handler_form is None:
                continue

            procedure = str(procedure_definition[1]) if len(procedure_definition) > 1 else "unknown"
            blurb = str(procedure_definition[3]) if len(procedure_definition) > 3 else ""
            label = str(procedure_definition[8]) if len(procedure_definition) > 8 else ""
            action = "Load" if handler_form[0] == "load-proc" else "Export"
            extensions = comma_values(form_value(handler_form, "extensions"))
            mime_types = comma_values(form_value(handler_form, "mime-types"))
            priority = form_value(handler_form, "priority", "0")

            flag_names = (
                ("handles-remote", "remote"),
                ("handles-uri", "URI"),
                ("handles-vector", "vector"),
                ("handles-raw", "raw"),
            )
            flags = [display for registry, display in flag_names if direct_form(handler_form, registry)]
            thumbnail = form_value(handler_form, "thumbnail-loader")
            if thumbnail:
                flags.append(f"thumbnail={thumbnail}")
            if priority not in ("", "0"):
                flags.append(f"priority={priority}")

            handlers.append(
                FileHandler(
                    action=action,
                    label=clean_label(label, blurb, procedure),
                    extensions=extensions,
                    mime_types=mime_types,
                    procedure=procedure,
                    plugin=plugin_name,
                    priority=priority,
                    flags=tuple(flags),
                )
            )

    if not handlers:
        raise RegistryError(f"no load or export handlers found in {path}")
    add_builtin_xcf_handlers(handlers)
    return handlers


def add_builtin_xcf_handlers(handlers: list[FileHandler]) -> None:
    """The native XCF handler is built into GIMP and is absent from pluginrc."""
    if any("xcf" in handler.extensions for handler in handlers):
        return
    common = {
        "label": "GIMP XCF image",
        "extensions": ("xcf",),
        "mime_types": ("image/x-xcf",),
        "plugin": "GIMP core",
        "priority": "",
        "flags": ("built-in",),
    }
    handlers.extend(
        (
            FileHandler(action="Load", procedure="gimp-file-load", **common),
            FileHandler(action="Save", procedure="gimp-file-save", **common),
        )
    )


def find_gimp(requested: str | None) -> str | None:
    if requested:
        expanded = os.path.expanduser(requested)
        return shutil.which(expanded) or (expanded if os.access(expanded, os.X_OK) else None)
    return shutil.which("gimp-console") or shutil.which("gimp")


def gimp_version(executable: str | None) -> str:
    if not executable:
        return "unknown version"
    try:
        result = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown version"
    output = (result.stdout or result.stderr).strip()
    match = re.search(r"(?:version\s+)?([0-9]+(?:\.[0-9]+)+)", output, re.IGNORECASE)
    return match.group(1) if match else output or "unknown version"


def registry_candidates() -> list[Path]:
    home = Path.home()
    xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    roots = [xdg_config / "GIMP", home / ".config" / "GIMP"]

    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "GIMP")
    roots.append(home / "Library" / "Application Support" / "GIMP")

    candidates: set[Path] = set()
    for variable in ("GIMP3_DIRECTORY", "GIMP2_DIRECTORY"):
        configured = os.environ.get(variable)
        if configured:
            configured_path = Path(configured).expanduser()
            candidates.add(configured_path / "pluginrc")
            candidates.add(xdg_config / "GIMP" / configured_path / "pluginrc")
    for root in roots:
        candidates.add(root / "pluginrc")
        candidates.update(root.glob("*/pluginrc"))
    candidates.update(home.glob(".gimp-*/pluginrc"))
    return [path for path in candidates if path.is_file()]


def newest_registry() -> Path | None:
    candidates = registry_candidates()
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def refresh_registry(executable: str) -> tuple[bool, str]:
    command = [
        executable,
        "--new-instance",
        "--no-interface",
        "--no-fonts",
        "--no-splash",
        "--no-shm",
        "--quit",
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "GIMP timed out after 60 seconds while refreshing its plug-in registry"
    except OSError as error:
        return False, f"could not run {executable}: {error}"

    if result.returncode == 0:
        return True, ""
    diagnostic = (result.stderr or result.stdout).strip().splitlines()
    detail = diagnostic[-1] if diagnostic else f"exit status {result.returncode}"
    return False, f"GIMP could not refresh its registry: {detail}"


def display_extensions(extensions: Iterable[str]) -> str:
    return ", ".join(f".{extension}" for extension in extensions) or "(magic/MIME only)"


def table_rows(
    handlers: Sequence[FileHandler], details: bool, show_all: bool
) -> tuple[list[str], list[list[str]]]:
    headers = ["Format"]
    if show_all:
        headers.append("Action")
    headers.extend(("Extensions", "MIME type(s)", "Procedure"))
    rows = [
        (
            [handler.label]
            + ([handler.action] if show_all else [])
            + [
                display_extensions(handler.extensions),
                ", ".join(handler.mime_types) or "-",
                handler.procedure,
            ]
        )
        for handler in handlers
    ]
    if details:
        headers.extend(("Flags", "Plug-in"))
        for row, handler in zip(rows, handlers):
            row.extend((", ".join(handler.flags) or "-", handler.plugin))
    return headers, rows


def choose_widths(headers: Sequence[str], rows: Sequence[Sequence[str]], width: int) -> list[int]:
    natural = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
    separators = 3 * (len(headers) - 1)
    available = max(width - separators, len(headers) * 8)
    column_limits = {
        "Format": (20, 38),
        "Action": (6, 8),
        "Extensions": (16, 32),
        "MIME type(s)": (18, 34),
        "Procedure": (20, 34),
        "Flags": (12, 28),
        "Plug-in": (16, 28),
    }
    minimums = [column_limits[header][0] for header in headers]
    maximums = [column_limits[header][1] for header in headers]
    widths = [min(size, maximum) for size, maximum in zip(natural, maximums)]

    while sum(widths) > available:
        candidates = [index for index, size in enumerate(widths) if size > minimums[index]]
        if not candidates:
            break
        largest = max(candidates, key=lambda index: widths[index] - minimums[index])
        widths[largest] -= 1
    return widths


def wrapped_lines(value: str, width: int) -> list[str]:
    return textwrap.wrap(
        value,
        width=max(width, 1),
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
    ) or [""]


def print_table(headers: Sequence[str], rows: Sequence[Sequence[str]], width: int) -> None:
    widths = choose_widths(headers, rows, width)
    print(" | ".join(header.ljust(size) for header, size in zip(headers, widths)))
    print("-+-".join("-" * size for size in widths))
    for row in rows:
        cells = [wrapped_lines(value, size) for value, size in zip(row, widths)]
        height = max(len(cell) for cell in cells)
        for line in range(height):
            print(
                " | ".join(
                    (cell[line] if line < len(cell) else "").ljust(size)
                    for cell, size in zip(cells, widths)
                )
            )


def filter_handlers(
    handlers: Iterable[FileHandler], show_all: bool, search: str | None
) -> list[FileHandler]:
    result = list(handlers)
    if not show_all:
        result = [handler for handler in result if handler.action == "Load"]

    if search:
        needle = search.casefold()
        result = [
            handler
            for handler in result
            if needle
            in " ".join(
                (
                    handler.action,
                    handler.label,
                    *handler.extensions,
                    *handler.mime_types,
                    handler.procedure,
                    handler.plugin,
                    *handler.flags,
                )
            ).casefold()
        ]

    action_order = {"Load": 0, "Save": 1, "Export": 2}
    return sorted(
        result,
        key=lambda handler: (
            handler.label.casefold(),
            action_order.get(handler.action, 9),
            handler.extensions,
            handler.procedure,
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List GIMP's currently registered load formats. Pass --all to include "
            "native-save and export handlers. By default GIMP is started headlessly "
            "to refresh its plug-in registry."
        )
    )
    parser.add_argument("--gimp", metavar="PATH", help="GIMP or gimp-console executable")
    parser.add_argument("--pluginrc", type=Path, help="parse this pluginrc without starting GIMP")
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="use the newest existing pluginrc instead of starting GIMP",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also show save/export handlers and the Action column",
    )
    parser.add_argument("--search", metavar="TEXT", help="only show matching rows")
    parser.add_argument("--details", action="store_true", help="also show flags and plug-in names")
    parser.add_argument("--width", type=int, help="output width (default: terminal width)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    executable = find_gimp(args.gimp)

    if args.pluginrc:
        registry = args.pluginrc.expanduser()
    else:
        if not executable and not args.no_refresh:
            print("error: gimp-console or gimp was not found in PATH", file=sys.stderr)
            return 2
        if executable and not args.no_refresh:
            refreshed, warning = refresh_registry(executable)
            if not refreshed:
                print(f"warning: {warning}", file=sys.stderr)
        registry = newest_registry()
        if registry is None:
            print(
                "error: no GIMP pluginrc was found; run without --no-refresh or pass --pluginrc",
                file=sys.stderr,
            )
            return 2

    try:
        all_handlers = parse_registry(registry)
    except RegistryError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    handlers = filter_handlers(all_handlers, args.all, args.search)
    version = gimp_version(executable)
    known_extensions = {extension for handler in all_handlers for extension in handler.extensions}
    counts = {
        action: sum(handler.action == action for handler in all_handlers)
        for action in ("Load", "Save", "Export")
    }

    print(f"GIMP {version} registered file formats")
    print(f"Registry: {registry}")
    print(
        f"Handlers: {len(all_handlers)} "
        f"({counts['Load']} load, {counts['Save']} native save, {counts['Export']} export); "
        f"{len(known_extensions)} distinct extensions"
    )
    if len(handlers) != len(all_handlers):
        qualifier = "matching " if args.search else ""
        scope = "handlers" if args.all else "load handlers"
        print(f"Showing: {len(handlers)} {qualifier}{scope}")
    print()

    if not handlers:
        print("No matching handlers.")
        return 0

    headers, rows = table_rows(handlers, args.details, args.all)
    terminal_width = shutil.get_terminal_size((160, 24)).columns
    output_width = max(args.width or terminal_width, 80)
    print_table(headers, rows, output_width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
