+++
schema_version = "0.1"

# One sentence, outcome-shaped: what is TRUE when this is done. Not the work.
goal = "TODO: <outcome sentence>"

# 5 for a single deterministic AC; 8 for multi-AC or path-uncertain work; >10 = two contracts.
iteration_cap = 8

# When must the agent STOP and escalate instead of guessing? Name the conditions
# and the escalation shape: attempted / evidence / blocker / next input.
blocked_stop = "TODO: <stop conditions + escalation shape>"

# Files, systems, actions the agent must NOT touch. At least one.
boundaries = [
  "Do not edit, broaden, or reinterpret acceptance criteria mid-build; changing AC requires kill and relaunch.",
  "TODO: <scope-specific boundary>",
]

# ── Repeat this block per acceptance criterion ────────────────────────────────
[[acceptance_criteria]]
id = "AC1"                      # AC1, AC2, ... — must match ^AC\d+$, unique
title = "TODO: <short label>"
given = "TODO: <preconditions the agent can arrange>"
when = "TODO: <trigger the agent can perform>"
then = "TODO: <outcome the agent can check>"

# REQUIRED — at least one per AC, or validation FAILS (V6). Never invent these.
# type: interview | ticket | usage_data | support | experiment | metric | other
[[acceptance_criteria.evidence]]
type = "TODO"
ref = "TODO: <URL, ticket ID, file path, or query reference>"
excerpt = "TODO: <the actual words or numbers, quoted — not summarized>"
date = "YYYY-MM-DD"             # optional but recommended

# ── Every AC id needs at least one of these; every entry must point at a real AC id ──
[[verification_surface]]
ac_id = "AC1"
type = "command"                # command | browser | manual
commands = ["TODO: <exact command, e.g. python3 -m unittest path.to.test -v>"]
expected_exit = 0

# type = "browser" variant:
# [[verification_surface]]
# ac_id = "AC2"
# type = "browser"
# url = "http://localhost:3000/path"
# expect = "DOM text that must be present"

# type = "manual" variant:
# [[verification_surface]]
# ac_id = "AC3"
# type = "manual"
# steps = ["open X", "do Y", "observe Z"]
# artifact = "path/to/screenshot-or-log.png"
+++

# Goal Contract — TODO: <issue/ID + short name>

<!--
Prose body: for humans, not validated. Suggested content:
- Context: where the request came from, in the requester's words.
- Evidence summary: the strongest quote/number per AC, with links.
- Cut list: what was refused or deferred for lack of evidence, and why.
- Decision history: anything ruled out during drafting.
Remember: the frontmatter is canonical. If prose and frontmatter disagree,
the frontmatter wins.
-->
