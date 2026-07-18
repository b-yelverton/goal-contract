# Specs are the new code. Intent needs provenance.

*Draft for Brett, pre-red-team. Placeholders marked `[[...]]`. Humanizer pass applied (29-pattern audit).*

---

## 1. The PRD was compiled for human engineers

For twenty years, the product requirements document has been a lossy
compression format. Product intent (what a user actually said, what the
numbers actually show) gets squeezed into prose that a human engineer
re-expands into code, filling the gaps with hallway conversations, taste, and
ten years of knowing what the PM probably meant. The gaps were load-bearing.
Humans are good at gaps.

Coding agents do not do hallway conversations.

When you hand an agent a PRD, it does not ask you what you meant. It builds
what you wrote, at machine speed, with perfect confidence, including the parts
you wrote carelessly at 11pm. The industry response has been to write better
specs: sharper prose, more structure, Given/When/Then everywhere. That helps.
It also misses the point, because the problem was never the spec's grammar.
The problem is that the spec arrives at the agent's door with no chain of
custody. Nothing in the artifact says *which line of this was ever true*: who
said it, when, in what words, with what numbers behind it.

The artifact an agent needs is not a document that persuades a human. It is a
contract that executes, with a finish line the agent can check by running
something and provenance a human can audit afterward. I have been running
such an artifact in my own dispatch system for months. This week I extracted
it into a standalone schema and a Claude Code skill, and I want five other
people to run it before I believe it.

## 2. A spec without evidence is just a prompt

Start with the honest part. Spec-driven development is the loudest
conversation in dev tooling right now, and the spec layer is good: GitHub's
Spec Kit has 122k stars and thirty agent integrations, AWS's Kiro turns
prompts into requirements, designs, and tasks, BMAD-METHOD has 50k stars and
a PM persona. If you want a free, well-maintained spec format, you are
spoiled. This is not a complaint about that layer, and what I built does not
compete with it.

But look at what those specs are made *from*. Every spec-half tool starts the
same way: an engineer types a prompt into an IDE. The spec is only ever as
true as that prompt. Meanwhile every PM-side tool (the ChatPRDs, the feedback
synthesizers, the discovery platforms) stops at a human-readable document.
Between "what users actually said" and "what the agent was told to build,"
there is exactly nothing. The discovery world and the spec world each end at
their own border. Intent crosses that border alone and loses fidelity at
every step.

That is the hole: a missing *bridge*, not a missing spec format. Intent with
provenance, compiled into whatever your agent harness already reads.

Why does provenance matter so much? Because agents fail differently than
humans. A human engineer who misunderstands a requirement wanders off for a
day and comes back with questions. An agent that misunderstands produces
thousands of lines of plausible, reviewable, *wrong*, and the wrongness
surfaces weeks later, when nobody can reconstruct why the requirement existed.
Without evidence attached to the requirement, you cannot even triage: was the
agent wrong, or was the spec wrong, or was the *request* wrong? A spec without
evidence is a prompt with ceremony. You would not merge code with no history;
you should not dispatch intent with no provenance.

## 3. The contract: seven fields, one of which is the point

The artifact is a **goal contract**: one Markdown file, machine-checkable
frontmatter on top, human prose below. Seven fields:

1. `goal`: one sentence, outcome-shaped. What is true in the world when this
   is done, not what work is performed.
2. `acceptance_criteria`: Given/When/Then scenarios. Each *Then* must name
   something an agent can check; if you cannot name the check, the criterion
   is not ready.
3. `verification_surface`: per criterion, the exact commands, browser checks,
   or manual artifacts that prove it passes. No executable surface, no
   dispatch.
4. `boundaries`: what the agent must not touch. Security-critical code,
   adjacent systems, the criteria themselves. The blast radius of being wrong.
5. `blocked_stop`: when the agent halts and escalates instead of guessing:
   a human-only ruling, a missing credential, a broken test harness. Plus the
   shape of the escalation: attempted, evidence, blocker, next input.
6. `iteration_cap`: an explicit attempt budget. Five for a deterministic
   change, eight for multi-criterion work. On exhaustion, the run stops
   honestly; it does not thrash silently and it does not declare itself done.
7. `evidence`: required, per acceptance criterion. Each criterion carries at
   least one link to the thing in the world that justifies it: the support
   ticket, the interview transcript, the usage query, with the actual words
   or numbers *quoted*, not summarized.

The seventh field is the product. The first six make a contract executable;
the seventh makes it *accountable*. And it is enforced mechanically: the
reference validator fails the contract (exit 1, no dispatch) if any criterion
lacks evidence. A refusal, not a lint warning.

The discipline cuts both ways. When I ran the schema's own smoke test,
feeding a raw feature request ("users keep asking for a CSV export of the
weekly digest") through the skill, the drafting agent quoted the support
ticket verbatim ("I paste it into our board pack manually every Friday"),
quoted the interview ("I don't want a dashboard, I want a file"), and quoted
the usage pull (37 of 210 workspaces, 4+ weeks running). Then it added a
security criterion nobody asked for (every request for an export is also a
request to scope that export to the right workspace) and, because the schema
forced it to cite evidence for that too, it had to stop and disclose in
prose: *not user-requested; mandatory engineering guardrail.* That disclosure
is the system working. Provenance keeps agents honest, and it keeps the
honest parts visible.

One more rule the schema enforces by culture rather than code: never invent
evidence. A contract with fabricated provenance is worse than no contract; it
launders a guess into a receipt. If a criterion has no evidence, that is a
*finding about the feature request*, and the correct move is to gather the
evidence or cut the criterion.

## 4. This runs nightly; next week it runs in public

This is not a proposal. I am a working PM, and the dispatch system this schema
was extracted from runs my own agent fleet nightly. Concretely, that system:

- compiles the contract from the issue **before the first model call** and
  persists it, so the contract never lives only in a prompt;
- hashes the acceptance criteria at compile time, so if the spec mutates
  mid-run the contract is *invalidated*: kill and relaunch rather than retcon
  the finish line;
- counts a criterion as done only when it has **fresh PASS evidence at the
  current branch SHA**; stale passes on old code do not count;
- on a blocked stop or an exhausted cap, posts what was attempted, what
  evidence was gathered, the specific blocker, and the next input needed. And
  the issue never advances on vibes.

The evidence field came out of a specific incident. A redelivered webhook
once queued a second agent against work already in flight: two agents, one
branch, two full turn budgets burned in sixty seconds. The fix, an atomic
admission guard, is in the system now, and its contract cites that incident
as evidence. That is the loop working as designed: the failure becomes a
link, the link becomes a criterion, the criterion becomes a test.

Next week I am running the full loop on my live product, in public: real user
feedback in → contract proposed with evidence → contract compiled → coding
agent implements unsupervised → I accept or reject against the criteria.
Everything documented. [[LINK TO WEEK-2 THREAD/REPO — Brett fills]]

## 5. The ask: five people, one feature each

The schema, a worked example, the Claude Code skill, and the validator are
public today: [[REPO URL — Brett fills]]. Files in, files out; no accounts, no
hosted anything.

What I do not have is other people's intent. So: I am looking for **five
working PMs or agent-heavy founders** to each run one real feature through
the loop in weeks 3–4. Bring a feature request and its evidence: tickets,
interviews, usage pulls. Run it through the skill (twenty minutes), hand the
contract to your coding agent, and tell me two numbers: what percentage of
the emitted contract you rewrote before dispatching, and whether you would
use it again.

My bar, set in advance: at least three of five dispatch with under 20%
rewrites and say they would use it again. Below that, this was a good blog
post and I will say so. Above it, the next artifacts are the compilers into
Spec Kit and Kiro formats; the contract is designed to land on their rails,
not replace them.

Signup: https://tally.so/r/QKaoxl — five seats, week of Aug 3 or Aug 10. If
you have ever watched an agent build the wrong thing beautifully, bring me
that feature.

---

*Brett Yelverton is a product manager who runs a home-built agent dispatch
system. The goal-contract schema is extracted from production code, not
invented for the post.*
