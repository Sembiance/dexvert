#!/usr/bin/env python3
# Vibe coded by Codex
"""List the import and export formats supported by the installed LibreOffice."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any

import uno
from com.sun.star.connection import NoConnectException


IMPORT = 1
EXPORT = 2


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        description="List formats supported by the installed LibreOffice."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="include export-only filters (hidden by default)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="show a summary count after the table",
    )
    return parser.parse_args()


def properties(registry: Any, name: str) -> dict[str, Any]:
    """Return a UNO registry entry as a regular dictionary."""
    return {property_.Name: property_.Value for property_ in registry.getByName(name)}


def connect_to_isolated_office(profile: pathlib.Path) -> tuple[Any, subprocess.Popen[str]]:
    """Start and connect to an isolated headless LibreOffice instance."""
    pipe_name = f"list_formats_{uuid.uuid4().hex}"
    process = subprocess.Popen(
        [
            "soffice",
            "--headless",
            "--nologo",
            "--nodefault",
            "--norestore",
            f"--accept=pipe,name={pipe_name};urp;StarOffice.ComponentContext",
            f"-env:UserInstallation={profile.as_uri()}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )

    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context
    )
    uno_url = f"uno:pipe,name={pipe_name};urp;StarOffice.ComponentContext"

    for _ in range(100):
        try:
            return resolver.resolve(uno_url), process
        except NoConnectException:
            if process.poll() is not None:
                error = process.stderr.read().strip() if process.stderr else ""
                raise RuntimeError(error or "LibreOffice exited before UNO was ready")
            time.sleep(0.05)

    process.terminate()
    process.wait(timeout=5)
    raise RuntimeError("Timed out while connecting to LibreOffice")


def display_width(text: str) -> int:
    """Return a practical terminal width for a Unicode string."""
    return len(text)


def print_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    """Print rows as an aligned, human-readable table."""
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], display_width(value))

    def render(row: tuple[str, ...]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row)).rstrip()

    print(render(headers))
    print(render(tuple("-" * width for width in widths)))
    for row in rows:
        print(render(row))


def main() -> int:
    arguments = parse_arguments()
    rows: list[tuple[str, ...]] = []
    office_context = None
    office_process = None

    try:
        with tempfile.TemporaryDirectory(prefix="soffice-list-formats-") as profile_name:
            profile = pathlib.Path(profile_name)
            office_context, office_process = connect_to_isolated_office(profile)
            service_manager = office_context.ServiceManager
            filters = service_manager.createInstanceWithContext(
                "com.sun.star.document.FilterFactory", office_context
            )
            types = service_manager.createInstanceWithContext(
                "com.sun.star.document.TypeDetection", office_context
            )

            for filter_name in filters.getElementNames():
                filter_properties = properties(filters, filter_name)
                flags = int(filter_properties.get("Flags", 0))
                if not flags & (IMPORT | EXPORT):
                    continue
                if not arguments.all and not flags & IMPORT:
                    continue

                type_properties: dict[str, Any] = {}
                type_name = filter_properties.get("Type", "")
                if type_name and types.hasByName(type_name):
                    type_properties = properties(types, type_name)

                capability = (
                    "Import/Export"
                    if flags & IMPORT and flags & EXPORT
                    else "Import"
                    if flags & IMPORT
                    else "Export"
                )
                extensions = ", ".join(type_properties.get("Extensions", ())) or "-"
                media_type = str(type_properties.get("MediaType", "")) or "-"
                display_name = str(filter_properties.get("UIName", ""))
                name = str(filter_name)
                if display_name and display_name != name:
                    name = f"{name} ({display_name})"

                if arguments.all:
                    rows.append((name, capability, extensions, media_type))
                else:
                    rows.append((name, extensions, media_type))

            rows.sort(key=lambda row: row[0].casefold())

            desktop = service_manager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", office_context
            )
            desktop.terminate()
            office_process.wait(timeout=10)

    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        if office_process is not None and office_process.poll() is None:
            office_process.terminate()
            try:
                office_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                office_process.kill()
                office_process.wait()
        print(f"Error: {error}", file=sys.stderr)
        return 1

    headers = (
        ("Name", "Capability", "Extensions", "MIME type")
        if arguments.all
        else ("Name", "Extensions", "MIME type")
    )
    print_table(headers, rows)
    if arguments.verbose:
        scope = "import/export" if arguments.all else "import-capable"
        print(f"\n{len(rows)} {scope} filter definitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
