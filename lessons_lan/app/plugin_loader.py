"""
Project: Homeschool Lessons (Dream.OS)
File: app/plugin_loader.py
Purpose: Lightweight local plugin loader (lesson generators, games, badges).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable

from flask import Flask


@dataclass(frozen=True)
class LoadedPlugin:
    name: str
    version: str
    module: Any


def _load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    # Ensure the module is visible during import-time side effects (e.g., dataclasses).
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_plugins(app: Flask) -> list[LoadedPlugin]:
    """
    Loads plugins from <project_root>/plugins/*/plugin.json with an entrypoint file.
    Keeps a list on app.extensions["plugins"].
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plugins_dir = os.path.join(project_root, "plugins")
    loaded: list[LoadedPlugin] = []

    if not os.path.isdir(plugins_dir):
        app.extensions["plugins"] = loaded
        return loaded

    for entry in sorted(os.listdir(plugins_dir)):
        plugin_path = os.path.join(plugins_dir, entry)
        if not os.path.isdir(plugin_path):
            continue
        manifest_path = os.path.join(plugin_path, "plugin.json")
        if not os.path.isfile(manifest_path):
            continue

        try:
            manifest = json.loads(open(manifest_path, "r", encoding="utf-8").read())
            name = str(manifest.get("name") or entry)
            version = str(manifest.get("version") or "0.0.0")
            entrypoint = str(manifest.get("entrypoint") or "plugin.py")
            entrypoint_path = os.path.join(plugin_path, entrypoint)
            if not os.path.isfile(entrypoint_path):
                continue

            module = _load_module_from_path(f"plugins.{name}", entrypoint_path)
            loaded.append(LoadedPlugin(name=name, version=version, module=module))
        except Exception as e:  # keep app booting even if a plugin fails
            app.logger.warning("Plugin load failed for %s: %s", entry, e)

    app.extensions["plugins"] = loaded
    return loaded


def call_first(app: Flask, fn_name: str, *args, **kwargs):
    """Call the first plugin that implements fn_name and return its result, else None."""
    plugins: list[LoadedPlugin] = app.extensions.get("plugins", [])
    for p in plugins:
        fn: Callable | None = getattr(p.module, fn_name, None)
        if callable(fn):
            return fn(*args, **kwargs)
    return None

