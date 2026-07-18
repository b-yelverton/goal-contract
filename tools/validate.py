#!/usr/bin/env python3
"""Reference validator for goal contract schema v0.1 (implements SCHEMA.md §4)."""

import re
import sys
import tomllib
from pathlib import Path

EVIDENCE_TYPES = {"interview", "ticket", "usage_data", "support", "experiment", "metric", "other"}
VERIFICATION_TYPES = {"command", "browser", "manual"}
TOP_LEVEL_KEYS = {"schema_version", "goal", "iteration_cap", "blocked_stop",
                  "boundaries", "acceptance_criteria", "verification_surface"}
AC_ID_RE = re.compile(r"^AC\d+$")
SENTENCE_END_RE = re.compile(r"[.!?](?:\s|$)")


def frontmatter_block(text):
    lines = text.splitlines()
    if not lines or lines[0] != "+++":
        return None
    for i in range(1, len(lines)):
        if lines[i] == "+++":
            return "\n".join(lines[1:i])
    return None


def blank(value):
    return not isinstance(value, str) or not value.strip()


def validate(path):
    errors, warnings = [], []
    err = lambda rule, msg: errors.append(f"ERROR {rule}: {msg}")
    warn = lambda rule, msg: warnings.append(f"WARN {rule}: {msg}")

    block = frontmatter_block(Path(path).read_text(encoding="utf-8"))
    if block is None:
        err("V1", "frontmatter block missing (first line must be '+++', closed by a later '+++' line)")
        return errors, warnings, {}
    try:
        data = tomllib.loads(block)
    except tomllib.TOMLDecodeError as e:
        err("V1", f"frontmatter TOML does not parse: {e}")
        return errors, warnings, {}

    for key in data:  # W4
        if key not in TOP_LEVEL_KEYS:
            warn("W4", f"unrecognized top-level key {key!r} (ignored for forward compatibility)")

    if data.get("schema_version") != "0.1":  # V2
        err("V2", f"schema_version missing or not \"0.1\" (got {data.get('schema_version')!r})")

    goal = data.get("goal")  # V3 / W1
    if blank(goal):
        err("V3", "goal missing or empty")
    else:
        if len(goal) > 300:
            warn("W1", f"goal exceeds ~300 characters ({len(goal)})")
        if len(SENTENCE_END_RE.findall(goal)) > 1:
            warn("W1", "goal appears to contain multiple sentences")

    boundaries = data.get("boundaries")  # V11
    if not isinstance(boundaries, list) or not boundaries:
        err("V11", "boundaries missing or empty")
    else:
        for i, b in enumerate(boundaries):
            if blank(b):
                err("V11", f"boundaries[{i}] is an empty string")

    if blank(data.get("blocked_stop")):  # V12
        err("V12", "blocked_stop missing or empty")

    cap = data.get("iteration_cap")  # V13 / W2
    if isinstance(cap, bool) or not isinstance(cap, int):
        err("V13", f"iteration_cap missing or not an integer (got {cap!r})")
    elif cap < 1:
        err("V13", f"iteration_cap < 1 (got {cap})")
    elif cap > 10:
        warn("W2", f"iteration_cap > 10 (got {cap})")

    acs = data.get("acceptance_criteria")  # V4
    if not isinstance(acs, list) or not acs:
        err("V4", "acceptance_criteria missing or empty")
        acs = []

    ac_ids, seen_ids, n_evidence = set(), {}, 0
    for idx, ac in enumerate(acs):
        if not isinstance(ac, dict):
            err("V5", f"acceptance_criteria[{idx}] is not a table")
            continue
        ac_id = ac.get("id")
        loc = f"acceptance_criteria[{ac_id if isinstance(ac_id, str) and ac_id else idx}]"
        if blank(ac_id):  # V5
            err("V5", f"{loc} missing 'id'")
        elif not AC_ID_RE.match(ac_id):
            err("V5", f"{loc} id {ac_id!r} does not match ^AC\\d+$")
        elif ac_id in seen_ids:
            err("V5", f"{loc} duplicates id of {seen_ids[ac_id]}")
        else:
            seen_ids[ac_id] = loc
            ac_ids.add(ac_id)
        for leg in ("given", "when", "then"):
            if blank(ac.get(leg)):
                err("V5", f"{loc} missing or empty '{leg}'")

        entries = ac.get("evidence")
        entries = entries if isinstance(entries, list) else []
        if not entries:  # V6
            err("V6", f"{loc} has zero evidence entries")
        for j, e in enumerate(entries):  # V7 / W3
            eloc = f"{loc}.evidence[{j}]"
            if not isinstance(e, dict):
                err("V7", f"{eloc} is not a table")
                continue
            n_evidence += 1
            for key in ("type", "ref", "excerpt"):
                if blank(e.get(key)):
                    err("V7", f"{eloc} missing or empty '{key}'")
            if isinstance(e.get("type"), str) and e["type"].strip() and e["type"] not in EVIDENCE_TYPES:
                err("V7", f"{eloc} type {e['type']!r} outside the evidence enum")
            if isinstance(e.get("excerpt"), str) and len(e["excerpt"]) > 280:
                warn("W3", f"{eloc} excerpt exceeds ~280 characters ({len(e['excerpt'])})")

    vs = data.get("verification_surface")
    covered = set()
    for j, v in enumerate(vs if isinstance(vs, list) else []):
        vloc = f"verification_surface[{j}]"
        if not isinstance(v, dict):
            err("V10", f"{vloc} is not a table")
            continue
        ref = v.get("ac_id")  # V8
        if blank(ref):
            err("V8", f"{vloc} missing 'ac_id' (references no declared AC)")
        elif ref not in ac_ids:
            err("V8", f"{vloc} references unknown AC id {ref!r}")
        else:
            covered.add(ref)
        t = v.get("type")  # V10
        if t not in VERIFICATION_TYPES:
            err("V10", f"{vloc} type {t!r} outside {{command, browser, manual}}")
            continue
        if t == "command":
            cmds = v.get("commands")
            if not isinstance(cmds, list) or not cmds or not all(isinstance(c, str) for c in cmds):
                err("V10", f"{vloc} (command) missing or malformed 'commands' (need non-empty list of strings)")
            ee = v.get("expected_exit", 0)
            if isinstance(ee, bool) or not isinstance(ee, int):
                err("V10", f"{vloc} (command) malformed 'expected_exit' (need integer)")
        elif t == "browser":
            for key in ("url", "expect"):
                if blank(v.get(key)):
                    err("V10", f"{vloc} (browser) missing or malformed '{key}'")
        elif t == "manual":
            steps = v.get("steps")
            if not isinstance(steps, list) or not steps or not all(isinstance(s, str) for s in steps):
                err("V10", f"{vloc} (manual) missing or malformed 'steps' (need non-empty list of strings)")
            if blank(v.get("artifact")):
                err("V10", f"{vloc} (manual) missing or malformed 'artifact'")

    for ac in acs:  # V9
        if isinstance(ac, dict) and isinstance(ac.get("id"), str) and AC_ID_RE.match(ac["id"]):
            if ac["id"] not in covered:
                err("V9", f"AC {ac['id']} has no verification_surface entry")

    stats = {"acs": sum(isinstance(a, dict) for a in acs), "evidence": n_evidence, "cap": cap}
    return errors, warnings, stats


def main(argv):
    if not argv:
        print("usage: python3 tools/validate.py <file> [<file> ...]", file=sys.stderr)
        return 1
    rc = 0
    for arg in argv:
        if not Path(arg).is_file():
            print(f"error: no such file: {arg}", file=sys.stderr)
            rc = 1
            continue
        errors, warnings, stats = validate(arg)
        for message in errors + warnings:
            print(f"{arg}: {message}")
        if errors:
            print(f"FAIL: {arg} — {len(errors)} error(s), {len(warnings)} warning(s)")
            rc = 1
        else:
            print(f"OK: {arg} compiles clean ({stats['acs']} ACs, {stats['evidence']} evidence entries, cap {stats['cap']})")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
