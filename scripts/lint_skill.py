"""Structural lint for a router skill.

Usage: python scripts/lint_skill.py skills/<stack>
"""
import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_LINES = 150
TOC_THRESHOLD = 100
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
REF_LINK_RE = re.compile(r"references/([a-z0-9-]+\.md)")
MD_LINK_RE = re.compile(r"\]\((?!https?:)[^)]*\.md\)")
REQUIRED_SECTIONS = ["## Existing repo", "## New repo default", "## Avoid", "## Sources"]


def _lint_skill_md(skill_dir: Path, errors: list[str]) -> set[str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_md}: missing")
        return set()
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        errors.append(f"{skill_md}: missing YAML frontmatter")
        return set()
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    name = str(meta.get("name", ""))
    if not NAME_RE.match(name):
        errors.append(f"SKILL.md: name '{name}' must be lowercase-hyphen, <= 64 chars")
    if name != skill_dir.name:
        errors.append(f"SKILL.md: name '{name}' must equal directory '{skill_dir.name}'")
    desc = str(meta.get("description", ""))
    if not desc or len(desc) > 1024:
        errors.append("SKILL.md: description must be 1..1024 chars")
    if len(body.splitlines()) > MAX_SKILL_LINES:
        errors.append(f"SKILL.md: body has {len(body.splitlines())} lines, max {MAX_SKILL_LINES}")
    return set(REF_LINK_RE.findall(body))


def _strip_code_fences(text: str) -> str:
    """Drop fenced code blocks so example content isn't read as headings or links."""
    kept, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def _lint_reference(path: Path, errors: list[str]) -> None:
    raw = path.read_text(encoding="utf-8")
    text = _strip_code_fences(raw)
    rel = f"references/{path.name}"
    if REF_LINK_RE.search(text) or MD_LINK_RE.search(text):
        errors.append(f"{rel}: links another reference (max one level deep)")
    if len(raw.splitlines()) > TOC_THRESHOLD and "## Contents" not in text:
        errors.append(f"{rel}: over {TOC_THRESHOLD} lines, needs '## Contents'")
    found = [h for h in re.findall(r"^## .+$", text, re.M) if h != "## Contents"]
    if found != REQUIRED_SECTIONS:
        errors.append(f"{rel}: sections {found} must be exactly {REQUIRED_SECTIONS}")
    sources = text.split("## Sources", 1)[1] if "## Sources" in text else ""
    if not re.search(r"^- https?://\S+", sources, re.M):
        errors.append(f"{rel}: ## Sources needs at least one '- https://…' line")


def _lint_evals(skill_dir: Path, on_disk: set[str], errors: list[str]) -> None:
    evals = skill_dir / "evals" / "routing.md"
    if not evals.exists():
        errors.append("evals/routing.md: missing")
        return
    expected: set[str] = set()
    negatives = 0
    for line in re.findall(r"^expect:\s*(.+)$", evals.read_text(encoding="utf-8"), re.M):
        items = [s.strip() for s in line.split(",") if s.strip()]
        if items == ["none"]:
            negatives += 1
        else:
            expected.update(items)
    for f in sorted(on_disk - expected):
        errors.append(f"evals: no eval expects references/{f}")
    for f in sorted(expected - on_disk):
        errors.append(f"evals: expects missing references/{f}")
    if negatives < 3:
        errors.append(f"evals: {negatives} negative evals (expect: none), need >= 3")


def lint(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    routed = _lint_skill_md(skill_dir, errors)
    ref_dir = skill_dir / "references"
    on_disk = {p.name for p in ref_dir.glob("*.md")} if ref_dir.exists() else set()
    if (skill_dir / "SKILL.md").exists():
        for f in sorted(routed - on_disk):
            errors.append(f"SKILL.md: router points to missing references/{f}")
        for f in sorted(on_disk - routed):
            errors.append(f"references/{f} not reachable from router")
    for f in sorted(on_disk):
        _lint_reference(ref_dir / f, errors)
    _lint_evals(skill_dir, on_disk, errors)
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/lint_skill.py skills/<stack>")
    errs = lint(Path(sys.argv[1]))
    for e in errs:
        print(e)
    print("OK" if not errs else f"{len(errs)} error(s)")
    sys.exit(1 if errs else 0)
