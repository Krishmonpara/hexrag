"""Load and merge layered YAML settings, resolving ${ENV:default} placeholders.

Profiles are selected with the HEXRAG_PROFILES env var (comma separated). The
"default" profile (settings.yaml) is always loaded first, then each named profile
(settings-<name>.yaml) is deep-merged on top, so later profiles win. This is how a
single config tree selects which concrete implementation each component uses.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


def settings_folder() -> Path:
    """Directory holding the settings*.yaml files.

    Defaults to the current working directory (run hexrag from the project root),
    overridable with HEXRAG_SETTINGS_FOLDER. Resolving relative to CWD rather than
    the package location keeps this correct for both editable and installed
    (copied) deployments.
    """
    return Path(os.environ.get("HEXRAG_SETTINGS_FOLDER", Path.cwd()))

# Matches ${VAR} or ${VAR:default} inside YAML scalar values.
_ENV_PATTERN = re.compile(r"\$\{(?P<name>[A-Za-z0-9_]+)(?::(?P<default>[^}]*))?\}")


def _active_profiles() -> list[str]:
    extra = [p.strip() for p in os.environ.get("HEXRAG_PROFILES", "").split(",") if p.strip()]
    # Preserve order, drop duplicates, always start from "default".
    seen: dict[str, None] = {}
    for profile in ["default", *extra]:
        seen.setdefault(profile, None)
    return list(seen)


def _resolve_env(value: Any) -> Any:
    """Recursively replace ${ENV:default} placeholders in strings."""
    if isinstance(value, str):

        def repl(match: re.Match[str]) -> str:
            return os.environ.get(match.group("name"), match.group("default") or "")

        return _ENV_PATTERN.sub(repl, value)
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env(v) for v in value]
    return value


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_profile(profile: str, folder: Path) -> dict[str, Any]:
    file_name = "settings.yaml" if profile == "default" else f"settings-{profile}.yaml"
    path = folder / file_name
    if not path.exists():
        raise FileNotFoundError(f"Settings file for profile '{profile}' not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise TypeError(f"Settings file has no top-level mapping: {path}")
    return _resolve_env(data)


def load_active_settings(folder: Path | None = None) -> dict[str, Any]:
    """Merge all active profiles into a single settings dict."""
    folder = folder or settings_folder()
    merged: dict[str, Any] = {}
    for profile in _active_profiles():
        merged = _deep_merge(merged, _load_profile(profile, folder))
    return merged
