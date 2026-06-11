#!/usr/bin/env python3

"""
Universal Version Checker

Usage:

    SCRIPT_VERSION = "1.0.0"

    from checkVersion import check_version
    check_version(SCRIPT_VERSION)

Remote version.txt format:

    version=1.2.0

    changes:
    - Fixed bug
    - Improved performance
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import requests

# =============================================================================
# COLORS
# =============================================================================

RESET = "\033[0m"

BOLD = "\033[1m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# =============================================================================
# CONFIG
# =============================================================================

CONFIG_FILE = Path(__file__).with_name("checkVersion.json")

DEFAULT_CONFIG = {
    "version_url": "",
    "timeout": 5,
    "show_up_to_date": False,
    "show_current_version": False,
}

# =============================================================================
# HELPERS
# =============================================================================


def load_config() -> dict:
    """
    Load configuration from JSON file.
    """

    config = DEFAULT_CONFIG.copy()

    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
    except Exception:
        pass

    return config


def normalize_version(version: str) -> tuple:
    """
    Supports:
        1
        1.0
        1.0.0
        1.0.0.1
        10.2.4.55
    """

    match = re.search(
        r"([0-9]+(?:\.[0-9]+)*)",
        str(version).strip()
    )

    if not match:
        raise ValueError(f"Invalid version: {version}")

    parts = [int(x) for x in match.group(1).split(".")]

    while len(parts) < 10:
        parts.append(0)

    return tuple(parts)


def github_repo_url(raw_url: str) -> str | None:
    """
    Convert:

    https://raw.githubusercontent.com/User/Repo/refs/heads/main/version.dat

    To:

    https://github.com/User/Repo
    """

    match = re.search(
        r"raw\.githubusercontent\.com/([^/]+)/([^/]+)/",
        raw_url
    )

    if not match:
        return None

    username = match.group(1)
    repository = match.group(2)

    return f"https://github.com/{username}/{repository}"


def parse_version_file(text: str) -> dict:
    """
    Parse version.txt
    """

    version_match = re.search(
        r"version\s*=\s*([0-9.]+)",
        text,
        re.IGNORECASE
    )

    if not version_match:
        raise ValueError("No version found")

    changes = []

    collecting = False

    for line in text.splitlines():

        if line.strip().lower().startswith("changes:"):
            collecting = True
            continue

        if collecting:

            line = line.strip()

            if not line:
                continue

            line = line.lstrip("-").strip()

            if line:
                changes.append(line)

    return {
        "version": version_match.group(1),
        "changes": changes,
    }


# =============================================================================
# NETWORK
# =============================================================================

@lru_cache(maxsize=1)
def get_remote_info() -> dict:

    config = load_config()

    url = config["version_url"]

    if not url:
        raise ValueError("No version URL configured")

    response = requests.get(
        url,
        timeout=config["timeout"]
    )

    response.raise_for_status()

    info = parse_version_file(response.text)

    info["repo_url"] = github_repo_url(url)

    return info


# =============================================================================
# DISPLAY
# =============================================================================

def print_update_message(
    current_version: str,
    latest_version: str,
    changes: list[str],
    repo_url: str | None
) -> None:

    print()

    print(
        f"{RED}{BOLD}"
        "╔══════════════════════════════════════════════════════╗"
    )

    print(
        "║                  UPDATE AVAILABLE                   ║"
    )

    print(
        "╚══════════════════════════════════════════════════════╝"
        f"{RESET}"
    )

    print(
        f"{WHITE}Current Version : "
        f"{YELLOW}{current_version}{RESET}"
    )

    print(
        f"{WHITE}Latest Version  : "
        f"{GREEN}{latest_version}{RESET}"
    )

    if changes:

        print()
        print(
            f"{CYAN}{BOLD}Changes:{RESET}"
        )

        for item in changes:
            print(f"  • {item}")

    if repo_url:

        print()
        print(
            f"{CYAN}{BOLD}Update:{RESET}"
        )

        print(repo_url)

    print()


# =============================================================================
# PUBLIC FUNCTION
# =============================================================================

def check_version(current_version: str) -> None:
    """
    Compare local version against remote version.
    """

    try:

        config = load_config()

        remote = get_remote_info()

        latest_version = remote["version"]

        current = normalize_version(
            current_version
        )

        latest = normalize_version(
            latest_version
        )

        if latest > current:

            print_update_message(
                current_version=current_version,
                latest_version=latest_version,
                changes=remote["changes"],
                repo_url=remote["repo_url"],
            )

        elif config["show_up_to_date"]:

            print(
                f"{GREEN}"
                f"Running latest version "
                f"({current_version})"
                f"{RESET}"
            )

        elif config["show_current_version"]:

            print(
                f"{CYAN}"
                f"Version: {current_version}"
                f"{RESET}"
            )

    except Exception:
        # Never break the script because
        # version checking failed.
        pass


if __name__ == "__main__":
    check_version("1.0.0")
