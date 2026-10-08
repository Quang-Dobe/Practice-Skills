import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lint_skill import lint

REF_OK = """# Title

> Load when: x.

## Existing repo
- a

## New repo default
- b

## Avoid
- c

## Sources
- https://learn.microsoft.com/x (fetched 2026-10-04)
"""

SKILL_OK = """---
name: demo
description: Demo skill. Use when testing the linter.
---

# Demo

| Task signal | Read |
|---|---|
| a | `references/a.md` |
| b | `references/b.md` |
"""

EVALS_OK = """## E01
prompt: do a
expect: a.md
must-not: none

## E02
prompt: do b
expect: b.md
must-not: none

## E03
prompt: n1
expect: none
## E04
prompt: n2
expect: none
## E05
prompt: n3
expect: none
"""


def make_skill(tmp_path, skill=SKILL_OK, refs=None, evals=EVALS_OK, name="demo"):
    d = tmp_path / name
    (d / "references").mkdir(parents=True)
    (d / "evals").mkdir()
    (d / "SKILL.md").write_text(skill, encoding="utf-8")
    for fname, body in (refs if refs is not None else {"a.md": REF_OK, "b.md": REF_OK}).items():
        (d / "references" / fname).write_text(body, encoding="utf-8")
    if evals is not None:
        (d / "evals" / "routing.md").write_text(evals, encoding="utf-8")
    return d


def test_valid_skill_passes(tmp_path):
    assert lint(make_skill(tmp_path)) == []


def test_missing_frontmatter(tmp_path):
    errs = lint(make_skill(tmp_path, skill="# no frontmatter\n"))
    assert any("frontmatter" in e for e in errs)


def test_name_must_match_dir(tmp_path):
    errs = lint(make_skill(tmp_path, name="other"))
    assert any("name" in e for e in errs)


def test_body_too_long(tmp_path):
    long_skill = SKILL_OK + "\n".join(f"line {i}" for i in range(200))
    errs = lint(make_skill(tmp_path, skill=long_skill))
    assert any("150" in e for e in errs)


def test_router_points_to_missing_file(tmp_path):
    errs = lint(make_skill(tmp_path, refs={"a.md": REF_OK}))
    assert any("missing references/b.md" in e for e in errs)


def test_orphan_reference(tmp_path):
    errs = lint(make_skill(tmp_path, refs={"a.md": REF_OK, "b.md": REF_OK, "c.md": REF_OK}))
    assert any("references/c.md not reachable" in e for e in errs)


def test_nested_reference_link(tmp_path):
    nested = REF_OK.replace("- a", "- see references/b.md")
    errs = lint(make_skill(tmp_path, refs={"a.md": nested, "b.md": REF_OK}))
    assert any("links another reference" in e for e in errs)


def test_long_reference_needs_contents(tmp_path):
    long_ref = REF_OK.replace("- a", "\n".join("- a" for _ in range(120)))
    errs = lint(make_skill(tmp_path, refs={"a.md": long_ref, "b.md": REF_OK}))
    assert any("## Contents" in e for e in errs)


def test_required_sections_in_order(tmp_path):
    bad = REF_OK.replace("## Avoid", "## Pitfalls")
    errs = lint(make_skill(tmp_path, refs={"a.md": bad, "b.md": REF_OK}))
    assert any("sections" in e for e in errs)


def test_sources_need_url(tmp_path):
    bad = REF_OK.replace("- https://learn.microsoft.com/x (fetched 2026-10-04)", "- docs")
    errs = lint(make_skill(tmp_path, refs={"a.md": bad, "b.md": REF_OK}))
    assert any("Sources" in e for e in errs)


def test_missing_evals(tmp_path):
    errs = lint(make_skill(tmp_path, evals=None))
    assert any("evals/routing.md" in e for e in errs)


def test_reference_without_eval(tmp_path):
    evals = EVALS_OK.replace("expect: b.md", "expect: a.md")
    errs = lint(make_skill(tmp_path, evals=evals))
    assert any("no eval expects references/b.md" in e for e in errs)


def test_needs_three_negatives(tmp_path):
    evals = EVALS_OK.split("## E04")[0]
    errs = lint(make_skill(tmp_path, evals=evals))
    assert any("negative" in e for e in errs)


def test_heading_inside_code_fence_is_ignored(tmp_path):
    fenced = REF_OK.replace("- b", "- b\n\n```markdown\n## Not a section\n```")
    assert lint(make_skill(tmp_path, refs={"a.md": fenced, "b.md": REF_OK})) == []


def test_reference_path_inside_code_fence_is_ignored(tmp_path):
    fenced = REF_OK.replace("- b", "- b\n\n```text\nsee references/b.md\n```")
    assert lint(make_skill(tmp_path, refs={"a.md": fenced, "b.md": REF_OK})) == []


def test_reference_link_outside_fence_still_fails(tmp_path):
    fenced = REF_OK.replace("- b", "- b\n\n```text\nok\n```\n\nsee references/b.md")
    errs = lint(make_skill(tmp_path, refs={"a.md": fenced, "b.md": REF_OK}))
    assert any("links another reference" in e for e in errs)
