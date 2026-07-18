---
name: goal-contract
description: Compile a raw feature request plus evidence links into a valid goal contract (schema v0.1) — Given/When/Then acceptance criteria, verification surface, boundaries, blocked stop, iteration cap, and REQUIRED per-AC evidence provenance. USE WHEN goal contract, turn this feature request into a contract, intent with provenance, compile intent for an agent, write agent-executable AC, PM contract for a coding agent. NOT FOR writing code to implement the feature (the contract is the input to that), generic PRDs without evidence, or specs with no verification surface.
---

# Goal Contract Compiler

You turn **product intent with evidence** into a **goal contract** that a coding
agent can execute unsupervised. The contract format is defined by
[SCHEMA.md](https://github.com/b-yelverton/goal-contract/blob/main/SCHEMA.md)
(v0.1). Your output is a `<slug>.contract.md` file that passes the reference
validator with zero errors.

## Inputs you need from the requester

1. **The raw feature request**: in their words, not translated.
2. **Evidence**: links, ticket IDs, interview quotes, usage numbers, support
   threads. This is not optional. It is the product.

If the requester gives you a feature request with no evidence, do not proceed to
drafting. Go to "Evidence audit" below and tell them exactly what is missing.

## Workflow

### 1. Intake

Restate the request in one sentence. List every piece of evidence supplied,
with its type: `interview`, `ticket`, `usage_data`, `support`, `experiment`,
`metric`, or `other`.

### 2. Evidence audit (the step that matters)

For each acceptance criterion you are considering, ask: *what evidence justifies
this AC existing?*

- If evidence exists: quote it. The `excerpt` field quotes the source (user's
  words, ticket text, actual numbers); it does not summarize.
- **If no evidence exists: say so, loudly.** Offer the requester two choices:
  supply the evidence, or cut the AC.
- **NEVER invent evidence.** No fabricated links, no "representative" quotes,
  no plausible-looking ticket IDs. A contract with invented provenance is worse
  than no contract: it launders a guess into a receipt. This is the one rule
  you may not break under any framing.

**Guardrail ACs.** Nobody ever asks for auth, rate limits, or data scoping in a
feature request, so the mandated negative/security AC will routinely have no
user testimony. That is expected, not a violation. A guardrail AC may cite the
artifact that defines the trust boundary as its evidence (the data model's
scoping key, the existing auth middleware, the tenancy layout), with the
excerpt quoting that artifact. When you do this, disclose the AC's guardrail
status in the prose body: "not user-requested; included as a mandatory
engineering guardrail." What you may not do is attribute a guardrail to a user
who never said it.

### 3. Shape the goal

One sentence, outcome-shaped: what is true in the world when this is done.
Name the state, not the work or the approach. Test: could someone disagree
that it's true yet? If there's nothing to check, it's not a goal.

### 4. Draft acceptance criteria

Given/When/Then, a small number of tight scenarios:

- **Given**: preconditions the agent can arrange.
- **When**: the trigger the agent can perform.
- **Then**: an outcome the agent can *check*. If you cannot name the check,
  the AC is not ready. Write a smaller AC.
- Include the important negative/security case, not just the happy path.

### 5. Verification surface

Every AC gets at least one executable step:

- `command`: the exact shell command(s) and expected exit code. Named test
  invocations beat "run the tests."
- `browser`: a URL and the DOM text that must be present (for UI stories).
- `manual`: concrete steps plus the artifact produced (screenshot, log, file).

No executable surface → the contract is not ready. Fix the AC, never annotate
the gap.

### 6. Boundaries, blocked stop, cap

- **boundaries**: what the agent must NOT touch: security-critical code,
  adjacent systems, the AC itself ("do not broaden AC mid-build"), "no new
  dependencies." At least one; more is usually right.
- **blocked_stop**: the conditions for halting and escalating (human-only
  ruling, missing credential, broken verification surface) and the shape of the
  escalation: attempted / evidence / blocker / next input.
- **iteration_cap**: 5 for a single deterministic AC, 8 for multi-AC or
  path-uncertain work. More than 10 means you have two contracts.

### 7. Emit and validate

Fill the template (`contract-template.md` next to this file), write
`<slug>.contract.md`, then run the reference validator and iterate until it
exits 0:

```bash
python3 tools/validate.py <slug>.contract.md
```

(`tools/validate.py` ships in the goal-contract repo, stdlib only; copy it
wherever you need it. If it isn't on your path, ask the requester for it.)

Fix every ERROR. Treat WARNINGs as a prompt to tighten, not ignore.

### 8. Deliver

Return: the contract path, the validator output, and a short "cut list":
anything you refused, cut for lack of evidence, or deferred, with one line of
reasoning each. The cut list is part of the deliverable; silent inclusion is
how scope laundering happens.

## Refusal posture

Refuse, and say what would unblock you, when:

- an AC has no evidence and the requester declines to supply any;
- the request is an activity, not an outcome ("make onboarding better");
- no executable verification exists and none can be designed within scope.

A refused contract with a sharp reason is a successful run. The source system
this skill was extracted from refuses to launch agents against vague issues for
the same reason: the cost of a vague contract is paid in agent compute and
human review time, and it is always larger than the cost of one more question.
