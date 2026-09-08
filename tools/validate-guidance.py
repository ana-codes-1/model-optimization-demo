#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / ".github" / "skills").glob("*/SKILL.md"))
AGENTS = sorted((ROOT / ".github" / "agents").glob("*.agent.md"))
MARKDOWN = sorted(
    [
        *ROOT.glob("*.md"),
        *(ROOT / ".github").rglob("*.md"),
        *(ROOT / "docs").rglob("*.md"),
    ]
)


def front_matter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.relative_to(ROOT)} has no front matter")
    _, metadata, _ = text.split("---", 2)
    for field in ("name:", "description:"):
        if field not in metadata:
            raise AssertionError(
                f"{path.relative_to(ROOT)} is missing front-matter field {field}"
            )
    return text


def validate_local_links() -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for document in MARKDOWN:
        for raw_target in link_pattern.findall(document.read_text(encoding="utf-8")):
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#", "/")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (document.parent / relative).exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")
    if broken:
        raise AssertionError(
            "Broken local Markdown links:\n- " + "\n- ".join(broken)
        )


def main() -> None:
    if not SKILLS:
        raise AssertionError("No EPS demo skills found")
    if len(AGENTS) < 2:
        raise AssertionError("Expected builder and release-reviewer agents")

    agents_guidance = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    prompt = (
        ROOT / ".github" / "prompts" / "new-demo.prompt.md"
    ).read_text(encoding="utf-8")

    for skill in SKILLS:
        front_matter(skill)
        skill_name = skill.parent.name
        if skill_name not in agents_guidance:
            raise AssertionError(f"AGENTS.md does not route {skill_name}")

    for agent in AGENTS:
        text = front_matter(agent)
        if "user-invocable: true" not in text:
            raise AssertionError(f"{agent.relative_to(ROOT)} is not user-invocable")
        if agent.name not in agents_guidance:
            raise AssertionError(f"AGENTS.md does not advertise {agent.name}")

    combined = "\n".join(
        [agents_guidance, prompt, *(path.read_text(encoding="utf-8") for path in SKILLS)]
    )
    required = (
        "DefaultAzureCredential",
        "Model Router",
        "negative",
        "health",
        "5xx",
        "served",
        "WSL",
    )
    for phrase in required:
        if not re.search(re.escape(phrase), combined, re.IGNORECASE):
            raise AssertionError(f"Guidance is missing required concept: {phrase}")

    contradictions = (
        "Operational Excellence — partner/customer concern, out of scope",
        "Public GitHub repo linked from the app.",
    )
    for phrase in contradictions:
        if phrase in combined:
            raise AssertionError(f"Outdated guidance remains: {phrase}")

    validate_local_links()
    print(
        f"Validated {len(SKILLS)} skills, {len(AGENTS)} agents, "
        f"{len(MARKDOWN)} Markdown files, AGENTS.md routing, and /new-demo coverage."
    )


if __name__ == "__main__":
    main()
