from __future__ import annotations

from typing import Any


def _is_valid(candidate: str) -> bool:
    if not (2 <= len(candidate) <= 30):
        return False
    for ch in candidate:
        if not (ch.isalnum() or ch in {"_", "."}):
            return False
    return True


def generate_suggestions(username: str, results: list[dict[str, Any]]) -> list[str]:
    key_platforms = {
        "GitHub",
        "Reddit",
        "TikTok",
        "X",
        "GitLab",
        "Bitbucket",
        "Dev.to",
        "CodePen",
        "Dribbble",
        "Behance",
    }
    needs_suggestions = any(
        r["platform"] in key_platforms and r["status"] != "available" for r in results
    )

    if not needs_suggestions:
        return []

    suffixes = ["hq", "dev", "app", "io", "official", "real"]
    separators = ["_", ".", "-"]
    numbers = ["01", "1", "2", "3"]

    candidates: list[str] = []
    seen = set()

    def push(value: str) -> None:
        if value in seen:
            return
        if not _is_valid(value):
            return
        seen.add(value)
        candidates.append(value)

    for suffix in suffixes:
        push(f"{username}{suffix}")
        for sep in separators:
            push(f"{username}{sep}{suffix}")

    for num in numbers:
        push(f"{username}{num}")
        for sep in separators:
            push(f"{username}{sep}{num}")

    push(f"its{username}")
    push(f"the{username}")
    push(f"{username}_dev")

    return candidates[:18]
