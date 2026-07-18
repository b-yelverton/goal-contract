# Goal Contract Schema v0.1

A **goal contract** is the smallest artifact that lets a coding agent implement a
product intent unsupervised — and lets a human verify, afterwards, *why* the agent
built what it built.

It is not a spec format. GitHub Spec Kit, AWS Kiro, and BMAD-METHOD already own
free spec formats, and they are good. A goal contract is the layer above them:
**intent with provenance**. Every acceptance criterion carries links to the
evidence that justifies it — the interview, the support ticket, the usage datum.
A contract that cannot trace every line of intent back to evidence does not
compile. That is the whole product thesis, and it is enforced mechanically
(rule **V6** below).

A goal contract compiles *into* whatever your agent harness already reads: a
Spec Kit spec, a Kiro steering file, a Claude Code prompt, a Linear issue. This
schema defines the source artifact, not the downstream renderings.

---

## 1. The seven fields

| # | Field | Required | Summary |
|---|-------|----------|---------|
| 1 | `goal` | **required** | One sentence, outcome-shaped. What is true when this is done. |
| 2 | `acceptance_criteria` | **required** | List of Given/When/Then scenarios. The finish line. |
| 3 | `verification_surface` | **required** | Per-AC: the exact commands, browser checks, or manual artifacts an agent runs to prove the AC passes. |
| 4 | `boundaries` | **required** | Files, systems, and actions the agent must not touch. |
| 5 | `blocked_stop` | **required** | Conditions under which the agent halts and escalates instead of guessing. |
| 6 | `iteration_cap` | **required** | Explicit maximum number of attempts. On exhaustion: honest stop, never silent thrash. |
| 7 | `evidence` | **required, per AC** | Provenance links for each acceptance criterion. **The differentiator.** |

The schema was generalized from a production dispatch system whose compiler
refuses to launch an agent against a vague issue, persists the contract before
the first model call, and iterates until every acceptance criterion has fresh
PASS evidence at the current branch SHA — or stops honestly at the cap. Field
lineage is in §6.

---

## 2. File format

A goal contract is a single Markdown file, conventionally named
`<slug>.contract.md`, with two parts:

1. **TOML frontmatter** between `+++` delimiter lines. This is the
   machine-readable contract and the **single source of truth**. Agents read
   this. Validators validate this.
2. **Prose body** below the frontmatter. Free-form context for humans: the
   narrative, links, screenshots, decision history. Humans read this. Nothing in
   the body is normative; if body and frontmatter disagree, the frontmatter
   wins.

TOML was chosen because it parses with the Python standard library alone
(`tomllib`, 3.11+) — validating a contract requires zero dependencies.

```text
+++
schema_version = "0.1"
goal = "..."
iteration_cap = 8
blocked_stop = "..."
boundaries = ["...", "..."]

[[acceptance_criteria]]
id = "AC1"
title = "..."
given = "..."
when = "..."
then = "..."

[[acceptance_criteria.evidence]]
type = "interview"
ref = "https://..."
excerpt = "..."

[[verification_surface]]
ac_id = "AC1"
type = "command"
commands = ["..."]
expected_exit = 0
+++

(Prose body for humans starts here.)
```

---

## 3. Field specification

### 3.1 `schema_version` — required, string

Must equal `"0.1"`. A validator that understands only v0.1 must reject anything
else rather than guess.

### 3.2 `goal` — required, string

One sentence, outcome-shaped: it names the state of the world that is true when
the contract is satisfied, not the work performed.

- Good: *"A build invoked twice against the same issue produces exactly one agent job."*
- Bad: *"Improve the dispatcher."* (activity, not outcome; unverifiable)

Validators must require a non-empty string and should warn when the goal is
longer than ~300 characters or reads as multiple sentences.

### 3.3 `acceptance_criteria` — required, list of tables

At least one criterion. Each criterion:

| Key | Required | Type | Rule |
|-----|----------|------|------|
| `id` | required | string | Matches `^AC\d+$`, unique within the contract. |
| `title` | recommended | string | Short human label. |
| `given` | required | string | Preconditions. Non-empty. |
| `when` | required | string | The trigger/action. Non-empty. |
| `then` | required | string | The verifiable outcome. Non-empty. |
| `evidence` | **required** | list of tables | **At least one entry. See §3.7.** |

Given/When/Then is not decoration. Each leg names something an agent can check:
a state it can arrange, an action it can perform, an assertion it can run. A
`then` that cannot be checked by the AC's verification step is a defect — write
a smaller AC.

### 3.4 `verification_surface` — required, list of tables

Every AC must be covered by at least one verification step, and every step must
reference an existing AC id. A criterion with no executable verification surface
must fail validation — an agent cannot be asked to prove what it cannot check.

| Key | Required | Type | Rule |
|-----|----------|------|------|
| `ac_id` | required | string | Must match a declared AC `id`. |
| `type` | required | string | One of `command`, `browser`, `manual`. |
| `commands` | if `command` | list of string | Shell commands run in order. |
| `expected_exit` | if `command` | integer | Expected exit code of the final command. Default `0`. |
| `url` | if `browser` | string | URL to load (typically localhost). |
| `expect` | if `browser` | string | DOM text that must be present. |
| `steps` | if `manual` | list of string | Human-executable check steps. |
| `artifact` | if `manual` | string | The produced artifact that proves the check ran (screenshot path, log file, report). |

`type = "none"` from earlier internal drafts is abolished. If an AC has no
executable check, the contract is not ready — fix the AC, don't annotate the
gap.

### 3.5 `boundaries` — required, list of strings

At least one entry. Each entry names a file, system, or action the agent must
not touch, or a scope rule it must not exceed. Boundaries are how a PM encodes
"the blast radius of being wrong."

Examples: `"Do not modify webhook signature verification."`, `"Do not broaden or
edit acceptance criteria mid-build; changing AC requires kill and relaunch."`,
`"No new third-party dependencies."`

### 3.6 `blocked_stop` — required, string

Non-empty. Names the conditions under which the agent must stop substantive
work and escalate rather than guess: a human-only ruling, a missing credential,
an exhausted quota, a failing verification surface. A good blocked_stop also
names the *shape* of the escalation: what was attempted, evidence gathered, the
specific blocker, and the next input needed.

### 3.7 `evidence` — **required, per AC**, list of tables

**This field is the product.** Every acceptance criterion must carry at least
one evidence entry tracing it to something that happened in the world: a user
said it, a ticket records it, a metric shows it. A contract whose ACs cannot be
traced to evidence is a prompt with extra steps, and this schema refuses to
compile it.

Each entry:

| Key | Required | Type | Rule |
|-----|----------|------|------|
| `type` | required | string | One of: `interview`, `ticket`, `usage_data`, `support`, `experiment`, `metric`, `other`. |
| `ref` | required | string | Resolvable pointer: URL, ticket ID, file path, or query reference. |
| `excerpt` | required | string | The actual words or numbers, quoted. ≤ ~280 characters (validators should warn beyond). |
| `date` | optional | string | ISO 8601 date of the evidence. |

Rules of the road:

- **Never invent evidence.** If an AC has no evidence, that is a finding about
  the feature request, not a gap to paper over. Either gather the evidence or
  cut the AC. Tools that emit contracts must mark missing evidence loudly, not
  fabricate plausible links.
- `excerpt` quotes the source, it does not summarize it. Provenance you cannot
  quote is provenance you do not have.
- `other` exists for honesty, not convenience. If half your entries are `other`,
  your evidence taxonomy or your discovery process is broken.

### 3.8 `iteration_cap` — required, integer

≥ 1. The maximum number of implementation/verification iterations the agent may
spend. When the cap is reached without all ACs passing, the run ends in an
honest terminal state — attempted work, evidence, blocker, and next input
posted — never in silent thrash and never in a false "done."

Guidance from the source system: single-scenario, deterministic changes cap at
5; multi-AC or path-uncertain work caps at 8. Validators should warn above 10 —
a contract that needs more than ten iterations is two contracts.

---

## 4. Validation rules

A contract **compiles clean** when a validator finds zero errors. Warnings do
not block compilation.

| Rule | Severity | Condition |
|------|----------|-----------|
| V1 | error | Frontmatter block missing, or TOML does not parse. |
| V2 | error | `schema_version` missing or not `"0.1"`. |
| V3 | error | `goal` missing or empty. |
| V4 | error | `acceptance_criteria` missing or empty. |
| V5 | error | An AC is missing `id`/`given`/`when`/`then`, has an `id` not matching `^AC\d+$`, or duplicates another AC's `id`. |
| **V6** | **error** | **An AC has zero `evidence` entries.** |
| V7 | error | An evidence entry is missing `type`/`ref`/`excerpt`, or `type` is outside the enum. |
| V8 | error | A `verification_surface` entry references an unknown AC `id`. |
| V9 | error | An AC has no `verification_surface` entry. |
| V10 | error | A verification step's `type` is outside `{command, browser, manual}`, or its type-specific required keys are missing or malformed. |
| V11 | error | `boundaries` missing, empty, or contains an empty string. |
| V12 | error | `blocked_stop` missing or empty. |
| V13 | error | `iteration_cap` missing, not an integer, or < 1. |
| W1 | warning | `goal` exceeds ~300 characters or appears to contain multiple sentences. |
| W2 | warning | `iteration_cap` > 10. |
| W3 | warning | An evidence `excerpt` exceeds ~280 characters. |
| W4 | warning | Unrecognized top-level key (forward compatibility: ignore, but say so). |

The reference validator is `tools/validate.py` in this repository. It implements
exactly these rules, prints errors and warnings with locations, and exits `0`
(clean) or `1` (errors present).

---

## 5. Lifecycle semantics (recommended, not validated)

The schema defines the artifact. The production system it was extracted from
adds four runtime behaviors that contract runners are encouraged to adopt:

1. **Compile before the first model call.** Persist the contract; do not let it
   live only in a prompt.
2. **AC-snapshot hashing.** Hash the sorted AC texts at compile time. If the
   acceptance criteria mutate mid-run, the contract is *invalidated* — kill and
   relaunch, never silently retcon the finish line.
3. **Fresh evidence at the current SHA.** An AC is done only when it has a PASS
   verification record at the current branch SHA. Stale passes on old code do
   not count. (Runtime verification records are deliberately a separate concept
   from the contract's `evidence` field: *evidence* is why the AC exists;
   *verification records* are proof the built thing satisfies it. v0.1 names the
   runtime artifact a **verification record** to keep the two from colliding.)
4. **Honest terminal states.** `done` (all ACs passing), `blocked` (escalated
   per `blocked_stop`), `cap_exhausted` (iteration cap reached). No fourth
   outcome, and "done" is never self-declared without verification records.

---

## 6. Lineage and license of ideas

v0.1 was generalized from two production modules of a private agent-dispatch
system:

- the **dispatcher compiler** (Linear issue → contract), which contributed the
  field set, the Given/When/Then parsing, the 5/8 turn-cap guidance, and the
  refusal to launch against non-executable acceptance criteria;
- the **goal-lifecycle loop**, which contributed compile-time persistence,
  AC-snapshot hashing, evidence-at-SHA freshness, and the
  blocked / cap-exhausted terminal states.

The `evidence` field (§3.7) exists in neither — it is the addition this schema
exists to make. The source system proves the loop runs; this schema bets that
provenance is what makes the loop worth running.

Downstream renderings are out of scope for v0.1: a Spec Kit preset, a Kiro
steering pack, and a hosted intake pipeline are all deliberately *not here yet*.
Files in, files out.
