# My agents kept building the wrong thing, so I started asking for receipts

*Specs are the new code. Intent needs provenance.*

---

## 1. The failure I kept paying for

I'm a PM by day. At night I run a small fleet of coding agents against my own
projects, and the failure mode I know best isn't the agent that crashes. It's
the agent that builds the wrong thing, beautifully. Two thousand lines that
compile, pass review, and solve a problem nobody has.

When a human engineer misunderstands a requirement, they wander off and come
back with questions. My agents come back with working code and total
confidence, and afterward I can't reconstruct which instruction of mine they
were obeying. The code isn't the expensive part. The expensive part is not
being able to answer a basic question: which line of what I asked for was
ever true?

Some of this is just what PRDs are. They were compiled for human engineers:
intent squeezed into prose, gaps filled by hallway conversations, taste, and
ten years of knowing what the PM probably meant. Humans are good at gaps.
Agents don't do hallway conversations. They build what you wrote, at machine
speed, including the parts you wrote carelessly at 11pm.

What I started doing, after one incident I'll get to: every requirement I
hand an agent has to carry its receipt. The ticket, the quote, the number
that caused it. This post is the artifact that fell out of that rule, how it
actually behaves, and where I think it's probably wrong. I'm posting it
because most of it cost me agent compute and one embarrassing evening to
learn, and it seems wasteful for everyone to learn it the same way.

## 2. What I found when I went looking

Before building anything, I went looking for who already solves this. The
spec tools are good: GitHub's Spec Kit (122k stars, thirty agent
integrations), AWS's Kiro, BMAD-METHOD (50k stars). Free, maintained, and not
something I'm competing with. But every one of them starts the same way: an
engineer types a prompt into an IDE. Spec Kit even ships a PM bundle, and
what it helps you do is write a better prompt. The spec is only ever as true
as that prompt.

The PM tools I know end at the other border. Feedback synthesizers, discovery
platforms: they produce a human-readable doc and stop. Between "what users
actually said" and "what the agent gets told to build," nothing carries the
why across. That's the gap I kept falling into.

So the rule I work from now: a spec without evidence is just a prompt. I'd
never merge code with no history. I got tired of dispatching intent with
none.

And when something does go wrong, provenance is what makes it triageable.
Without it, I can't tell whether the agent was wrong, the spec was wrong, or
the request was wrong. Those have completely different fixes, and I was
guessing which one to apply.

## 3. The contract

The artifact that fell out is a goal contract: one Markdown file,
machine-checkable frontmatter on top, human prose below. Seven fields:

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

The seventh field is why I'm writing this post. The first six make a contract
executable. The seventh makes it checkable, and it's enforced mechanically:
the validator fails the contract (exit 1, no dispatch) if any criterion lacks
evidence. A refusal, not a lint warning.

You can watch the gate work in about thirty seconds, on your own machine:
clone the repo, delete the evidence block under AC2 in the example contract,
and the validator exits 1: `ERROR V6: acceptance_criteria[AC2] has zero
evidence entries`. No dispatch, no agent, no exceptions. That example's AC2
also carries a real receipt: it cites the incident that caused it. The link
is marked illustrative because my tracker is private, but the incident is
real, and it's the next section's story, because it's the reason this field
exists.

The posture isn't new for me; it's how the dispatcher already handled
vagueness. Ask it to build a loose issue and it refuses, and the refusal
hands back a draft: *Acceptance criteria are missing or not executable.
Draft G/W/T AC: Given the intended user and current repo context are
explicit; When the requested change is implemented; Then the named behavior
is verifiably true with a concrete command or manual check.* Issues come
back better the second time. The evidence field points the same refusal at a
different question: not "can an agent check this?" but "why does this
criterion exist at all?"

Now the honest limit, because it's the first thing a skeptical reader should
ask about: the validator checks that a link exists, not that the link is
true. I can't make a tool verify that a quote is real, and I won't pretend
otherwise. What I can do is make fabrication leave fingerprints. The excerpt
field forces the actual words to be written down, attached to a source, next
to the criterion they claim to justify. Presence is mechanical; truth is
audit; and audit is cheap precisely because everything is quoted in place. A
hallucinated PRD leaves no trail at all. A fabricated receipt leaves a
written one, in the author's own hand.

The companion rule is cultural, and I'd rather say that plainly than dress it
up: never invent evidence. If a criterion has no evidence, that's a finding
about the feature request, and the right move is to gather the evidence or
cut the criterion. A schema can make lying visible. It can't make people
honest. I think that's still worth having.

## 4. It runs every night, and I know you can't check that

The schema isn't a proposal. It was extracted from a dispatch system I run
against my own agent fleet every night. That system:

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

You can't inspect any of that. The system is private, tangled in my homelab,
and full of references to people and products that aren't mine to share. So
it's n=1, self-reported, by the person selling the schema. Grade the repo
instead: the example contract in it is reconstructed from the system's real
test fixtures, and the validator runs on your machine in seconds. And it's
why next week I'm running the whole loop in public, on my live product: real
feedback in → contract proposed with evidence → contract compiled → coding
agent implements unsupervised → I accept or reject against the criteria.
Everything documented; the loop diary publishes here as it happens.

The evidence field itself came out of an incident, not a principle. A
redelivered webhook once queued a second agent against work already in
flight: two agents, one branch, two full turn budgets burned in sixty
seconds. The fix, an atomic admission guard, is in the system now, and its
contract cites that incident as evidence. That's the loop working the way I
want it to: the failure becomes a link, the link becomes a criterion, the
criterion becomes a test.

## 5. What I'm asking

What I don't have is other people's intent. So I'm looking for five working
PMs or agent-heavy founders to each run one real feature through the loop in
weeks 3–4. Bring a feature request and its evidence: tickets, interviews,
usage pulls. Run it through the skill (twenty minutes), hand the contract to
your coding agent, and tell me two numbers: what percentage of the contract
you rewrote before dispatching, and whether you'd use it again.

My bar, set in advance: at least three of five dispatch with under 20%
rewrites and say they'd use it again. Below that, this was a good blog post
and I'll say so. Above it, the next artifacts are the compilers into Spec Kit
and Kiro formats; the contract is designed to land on their rails, not
replace them.

And if one of those teams ships an evidence field first: good. The pattern
matters more than my implementation of it. I'd just like it to start here.

The schema, a worked example, the skill, and the validator are public today:
https://github.com/b-yelverton/goal-contract. Files in, files out; no
accounts, no hosted anything.

Signup: https://tally.so/r/QKaoxl — five seats, week of Aug 3 or Aug 10. If
you've ever watched an agent build the wrong thing beautifully, bring me that
feature. I'd like to learn from it.

---

*Brett Yelverton is a product manager who runs a home-built agent dispatch
system at night. The goal-contract schema is extracted from that system, not
invented for this post.*
