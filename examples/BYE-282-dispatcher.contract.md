+++
schema_version = "0.1"
goal = "Dispatching a Linear build command compiles the issue's acceptance criteria into a persisted goal contract, and a duplicate dispatch never starts a second agent."
iteration_cap = 8
blocked_stop = "Stop substantive work and escalate if: the Linear webhook secret or other credential is unavailable; the AC cannot be made executable without a product ruling from Brett; or the verification surface itself fails (test harness broken). Post: what was attempted, evidence gathered, the specific blocker, and the next input needed. Never move the issue to In Review unless every AC has a fresh PASS at the current branch SHA."
boundaries = [
  "Do not modify webhook signature verification (HMAC + timestamp tolerance) — security-critical and out of scope.",
  "Do not edit, broaden, or reinterpret acceptance criteria mid-build; changing AC requires kill and relaunch.",
  "Do not weaken, skip, or delete existing tests to make a check pass.",
  "Do not touch the goal-lifecycle module's persisted state format in this build.",
  "Keep all commits, the branch, and the PR linked to the Linear issue identifier.",
]

[[acceptance_criteria]]
id = "AC1"
title = "Expected flow"
given = "A Linear issue with executable Given/When/Then acceptance criteria and explicit repo context"
when = "The operator invokes the build command against that issue in Claude Code or Codex"
then = "The launcher compiles outcome, verification surface, constraints, boundaries, iteration policy, and blocked stop condition into a goal contract written into the agent's prompt"

[[acceptance_criteria.evidence]]
type = "ticket"
ref = "https://linear.app/byelverton/issue/BYE-278 (illustrative — private system)"
excerpt = "I want every build to launch with a goal contract. Today the agent gets the raw issue text and improvise its own finish line; the finish line should be compiled, not improvised."
date = "2026-06-24"

[[acceptance_criteria.evidence]]
type = "support"
ref = "agent-config/tests/linear_dispatch/test_dispatcher.py :: test_build_contract_compiles_acceptance_criteria_into_goal_prompt (real — this repo's sibling test suite)"
excerpt = "assertIn('## Goal Contract', prompt); assertIn('Outcome: satisfy all executable acceptance criteria for BYE-282', prompt); assertIn('Blocked stop condition', prompt)"

[[acceptance_criteria]]
id = "AC2"
title = "Duplicate dispatch guard"
given = "A build agent is already working the issue under an active goal contract"
when = "The operator invokes the build command against the same issue again (retry, double-click, or webhook redelivery)"
then = "The launcher does not start a second agent; it reports the existing job, its tool and session, and offers resume-or-explicitly-kill"

[[acceptance_criteria.evidence]]
type = "metric"
ref = "dispatcher state: jobs.sqlite admissions log, 2026-06-30 incident (illustrative — private system)"
excerpt = "Same AgentSession activity delivered twice within 60 s produced two queued build jobs for BYE-282; both agents burned a full turn budget against the same branch."

[[acceptance_criteria.evidence]]
type = "ticket"
ref = "https://linear.app/byelverton/issue/BYE-327 (illustrative — private system)"
excerpt = "Atomic admission prevents duplicate jobs under concurrent delivery: 20 concurrent deliveries of the same activity must produce exactly one job."
date = "2026-07-02"

[[verification_surface]]
ac_id = "AC1"
type = "command"
commands = [
  "python3 -m unittest tests.linear_dispatch.test_dispatcher.LinearDispatcherTests.test_build_contract_compiles_acceptance_criteria_into_goal_prompt -v",
]
expected_exit = 0

[[verification_surface]]
ac_id = "AC2"
type = "command"
commands = [
  "python3 -m unittest tests.linear_dispatch.test_dispatcher.AdmissionIdempotencyTests.test_concurrent_deliveries_with_same_activity_create_exactly_one_job -v",
]
expected_exit = 0
+++

# Goal Contract — BYE-282: Build dispatcher

*Example contract for schema v0.1. The feature is real: it is the dispatch
compiler this schema was extracted from, reconstructed from its own test
fixtures. Evidence entries that point at Brett's private Linear instance are
marked illustrative. The test-suite pointer is a real, resolvable reference.*

## Context

The dispatch system turns Linear comments (`@Codex build`) into queued agent
jobs. Before this feature, the agent received the raw issue and improvised its
own definition of done; redelivered webhooks could also queue a second agent
against work already in flight.

## Why these two ACs

AC1 is the core behavior: the contract is *compiled*, so the finish line is
fixed before the first model call, not negotiated mid-run. AC2 is the failure
mode that cost real money: one duplicate webhook delivery, two agents, one
branch. Both ACs trace to evidence: an operator ticket for the behavior, and an
admissions-log incident plus a concurrency ticket for the guard. If either link
breaks, the AC is suspect. That is the point of the field.
