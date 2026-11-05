"""Checks the semantic model's names against the model-standards rules.

    python check_names.py [folder ...]   checks every TMDL file (default: every *.SemanticModel)
    python check_names.py --hook         run by a hook: checks only the file just edited
"""
import json
import pathlib
import re
import sys


def check(file):
    problems = []
    lines = file.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"\s*(table|column|measure)\s+('([^']+)'|[^\s=]+)", line)
        if not m:
            continue
        kind, name = m.group(1), m.group(3) or m.group(2)
        if "_" in name:
            problems.append(f"{file.name}: {kind} '{name}' has an underscore")
        if kind == "measure" and not lines[i - 1].strip().startswith("///"):
            problems.append(f"{file.name}: measure '{name}' has no description")
    return problems


if "--hook" in sys.argv:
    edited = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    if edited.endswith(".tmdl") and pathlib.Path(edited).exists():
        problems = check(pathlib.Path(edited))
        if problems:
            print("\n".join(problems), file=sys.stderr)  # a hook shows this to the agent
            sys.exit(2)
    sys.exit(0)

folders = [pathlib.Path(a) for a in sys.argv[1:]] or list(pathlib.Path(".").glob("*.SemanticModel"))
problems = [p for folder in folders for f in sorted(folder.rglob("*.tmdl")) for p in check(f)]
print("\n".join(problems) or "No problems found")
