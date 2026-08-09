#!/usr/bin/env -S calibre-debug -e -- --
# Vibe coded by Codex
"""List the conversion formats supported by the installed Calibre version.

The script intentionally obtains all format extensions and descriptive metadata
from Calibre at runtime.  Run it directly, or with:

    calibre-debug -e calibreListFormats.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
from pathlib import Path

import calibre
from calibre.customize.ui import (
    available_input_formats,
    available_output_formats,
    initialized_plugins,
    input_format_plugins,
    output_format_plugins,
)


MINIMUM_TABLE_WIDTH = 88
MAXIMUM_TABLE_WIDTH = 180


def normalized_text(value: object) -> str:
    """Turn plug-in metadata into clean, single-line display text."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalized_formats(values: object) -> set[str]:
    """Normalize a Calibre collection of extensions."""
    if not values:
        return set()
    return {
        normalized_text(value).lower().lstrip(".")
        for value in values
        if normalized_text(value)
    }


def version_text(value: object) -> str:
    """Format tuple-style and string-style plug-in versions consistently."""
    if isinstance(value, (tuple, list)):
        return ".".join(str(part) for part in value)
    return normalized_text(value) or "-"


def plugin_formats(plugin: object, direction: str) -> set[str]:
    """Read extensions from either an input or output plug-in."""
    if direction == "input":
        return normalized_formats(getattr(plugin, "file_types", ()))

    value = getattr(plugin, "file_type", None)
    if value:
        return normalized_formats((value,))
    return normalized_formats(getattr(plugin, "file_types", ()))


def completion_formats() -> tuple[set[str], set[str], str]:
    """Read Calibre's generated ebook-convert completion database, if present."""
    try:
        from calibre.utils.resources import get_path
        from calibre.utils.serialize import msgpack_loads

        resource_path = Path(
            get_path(
                "ebook-convert-complete.calibre_msgpack",
                allow_user_override=False,
            )
        )
        data = msgpack_loads(resource_path.read_bytes(), use_list=False)
        inputs = normalized_formats(data.get("input_fmts", ()))
        outputs = normalized_formats(data.get("output", ()))
        return inputs, outputs, str(resource_path)
    except (ImportError, OSError, TypeError, ValueError, AttributeError) as error:
        return set(), set(), f"unavailable ({normalized_text(error)})"


def plugin_record(plugin: object, extensions: set[str]) -> dict[str, str]:
    """Create a printable record from a Calibre plug-in object."""
    return {
        "name": normalized_text(getattr(plugin, "name", "")) or "Unnamed plug-in",
        "extensions": ", ".join(extension.upper() for extension in sorted(extensions)),
        "kind": normalized_text(getattr(plugin, "type", "")) or "Plug-in",
        "version": version_text(getattr(plugin, "version", None)),
        "author": normalized_text(getattr(plugin, "author", "")) or "-",
        "description": normalized_text(getattr(plugin, "description", "")) or "-",
    }


def fallback_record(extensions: set[str], direction: str) -> dict[str, str]:
    """Describe formats advertised by Calibre but not owned by a plug-in."""
    label = "Built-in special input" if direction == "input" else "Built-in output"
    return {
        "name": label,
        "extensions": ", ".join(extension.upper() for extension in sorted(extensions)),
        "kind": "Conversion metadata",
        "version": "-",
        "author": "Calibre",
        "description": (
            "Advertised by ebook-convert's installed completion metadata; "
            "no enabled plug-in claims the extension directly."
        ),
    }


def supporting_plugin_records(extensions: set[str]) -> list[dict[str, str]]:
    """Match special input extensions to non-conversion Calibre plug-ins."""
    remaining = set(extensions)
    records: list[dict[str, str]] = []
    candidates = []

    for plugin in initialized_plugins():
        kind = normalized_text(getattr(plugin, "type", ""))
        if kind.startswith("Conversion "):
            continue
        claimed = normalized_formats(getattr(plugin, "file_types", ()))
        overlap = claimed & remaining
        if overlap:
            candidates.append((kind != "File type", kind.casefold(), plugin, claimed))

    for _not_file_type, _kind, plugin, claimed in sorted(
        candidates,
        key=lambda item: (item[0], item[1], normalized_text(item[2].name).casefold()),
    ):
        overlap = claimed & remaining
        if not overlap:
            continue
        records.append(plugin_record(plugin, overlap))
        remaining -= overlap

    if remaining:
        records.append(fallback_record(remaining, "input"))
    return records


def conversion_records(
    plugins: object,
    direction: str,
) -> tuple[list[dict[str, str]], set[str]]:
    """Collect records and the union of extensions claimed by conversion plug-ins."""
    records: list[dict[str, str]] = []
    claimed_formats: set[str] = set()

    for plugin in plugins:
        extensions = plugin_formats(plugin, direction)
        if not extensions:
            continue
        claimed_formats |= extensions
        records.append(plugin_record(plugin, extensions))

    return records, claimed_formats


def wrap_cells(row: list[str], widths: list[int]) -> list[list[str]]:
    """Wrap one logical row into one or more physical table rows."""
    wrapped = []
    for value, width in zip(row, widths):
        lines = textwrap.wrap(
            value,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        wrapped.append(lines)

    height = max(len(lines) for lines in wrapped)
    return [
        [wrapped[column][line] if line < len(wrapped[column]) else "" for column in range(len(row))]
        for line in range(height)
    ]


def column_layout(
    total_width: int,
    show_metadata: bool,
) -> tuple[list[str], list[str], list[int]]:
    """Choose columns and widths appropriate for the current terminal."""
    if not show_metadata:
        headers = ["Format / provider", "Extensions", "Description"]
        keys = ["name", "extensions", "description"]
        fixed = [24, 24]
    else:
        headers = ["Format / provider", "Extensions", "Kind", "Version", "Author", "Description"]
        keys = ["name", "extensions", "kind", "version", "author", "description"]
        fixed = [23, 22, 19, 9, 18]

    separator_width = 3 * (len(headers) - 1)
    description_width = total_width - separator_width - sum(fixed)
    return headers, keys, fixed + [description_width]


def print_table(
    records: list[dict[str, str]],
    total_width: int,
    show_metadata: bool,
) -> None:
    """Print plug-in records as an aligned, wrapped table."""
    headers, keys, widths = column_layout(total_width, show_metadata)

    def print_physical_row(values: list[str]) -> None:
        print(" | ".join(value.ljust(width) for value, width in zip(values, widths)).rstrip())

    print_physical_row(headers)
    print("-+-".join("-" * width for width in widths))

    for record in records:
        logical_row = [record[key] for key in keys]
        for physical_row in wrap_cells(logical_row, widths):
            print_physical_row(physical_row)


def sorted_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sort records by their first extension and then provider name."""
    return sorted(
        records,
        key=lambda record: (
            record["extensions"].casefold(),
            record["name"].casefold(),
        ),
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="List formats supported by the installed Calibre version.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also show supported output formats",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    completion_inputs, completion_outputs, completion_source = completion_formats()

    input_records, plugin_inputs = conversion_records(input_format_plugins(), "input")
    output_records, plugin_outputs = conversion_records(output_format_plugins(), "output")

    all_inputs = (
        normalized_formats(available_input_formats())
        | plugin_inputs
        | completion_inputs
    )
    all_outputs = (
        normalized_formats(available_output_formats())
        | plugin_outputs
        | completion_outputs
    )

    input_records.extend(supporting_plugin_records(all_inputs - plugin_inputs))
    uncovered_outputs = all_outputs - plugin_outputs
    if uncovered_outputs:
        output_records.append(fallback_record(uncovered_outputs, "output"))

    terminal_width = shutil.get_terminal_size((140, 24)).columns
    minimum_width = 130 if arguments.all else MINIMUM_TABLE_WIDTH
    table_width = min(MAXIMUM_TABLE_WIDTH, max(minimum_width, terminal_width))

    print(f"Calibre {calibre.__version__} ebook-convert formats")
    print("Data source: installed plug-in registry and generated completion metadata")
    print(f"Completion metadata: {completion_source}")

    print(f"\nINPUT FORMATS: {len(all_inputs)} extensions across {len(input_records)} providers")
    print_table(sorted_records(input_records), table_width, arguments.all)

    if arguments.all:
        print(f"\nOUTPUT FORMATS: {len(all_outputs)} extensions across {len(output_records)} providers")
        print_table(sorted_records(output_records), table_width, True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
