"""Public entrypoints for the toolbar application."""

from __future__ import annotations

from .app import ToolbarApp


def main() -> None:
    """Start the toolbar application."""

    ToolbarApp().run()


__all__ = ["main", "ToolbarApp"]
