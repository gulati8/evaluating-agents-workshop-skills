#!/usr/bin/env python3
"""Render conventions.json into a self-contained review form (conventions.html).

Usage: python3 render_form.py <conventions.json> <conventions.html>

Standard library only. The form works as a local file opened in a browser:
decisions are kept in the browser's localStorage per repo and exported as
JSON with the Copy or Download buttons.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "form_template.html"

REQUIRED_TOP = {"repo", "generated_at", "profile", "conventions"}
REQUIRED_RULE = {
    "id", "assertion", "mechanism", "category", "confidence", "why_it_matters",
    "evidence", "counter_examples", "check", "check_detail",
}
CHECKS = {"reading", "test", "judgment"}
CONF = {"high", "medium", "low"}


def validate(data):
    problems = []
    missing = REQUIRED_TOP - set(data)
    if missing:
        problems.append(f"top level missing: {sorted(missing)}")
        return problems
    if not isinstance(data["conventions"], list) or not data["conventions"]:
        problems.append("conventions must be a non-empty list")
        return problems
    seen = set()
    for i, c in enumerate(data["conventions"]):
        where = f"conventions[{i}] ({c.get('id', '?')})"
        miss = REQUIRED_RULE - set(c)
        if miss:
            problems.append(f"{where} missing: {sorted(miss)}")
            continue
        if c["id"] in seen:
            problems.append(f"{where} duplicate id")
        seen.add(c["id"])
        if c["check"] not in CHECKS:
            problems.append(f"{where} check must be one of {sorted(CHECKS)}")
        if c["confidence"] not in CONF:
            problems.append(f"{where} confidence must be one of {sorted(CONF)}")
        if not c["evidence"]:
            problems.append(f"{where} has no evidence")
    return problems


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src, dst = Path(argv[1]), Path(argv[2])
    data = json.loads(src.read_text(encoding="utf-8"))
    problems = validate(data)
    if problems:
        print("conventions.json is not in the expected shape:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__DATA__*/null", payload, 1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html, encoding="utf-8")
    n = len(data["conventions"])
    by_check = {k: sum(1 for c in data["conventions"] if c["check"] == k) for k in sorted(CHECKS)}
    print(f"wrote {dst} ({n} conventions; " + ", ".join(f"{k} {v}" for k, v in by_check.items()) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
