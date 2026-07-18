# goal-contract

**Specs are the new code — but a spec without evidence is just a prompt.** A
goal contract is the smallest artifact that lets a coding agent implement
product intent unsupervised: seven fields (goal, Given/When/Then acceptance
criteria, verification surface, boundaries, blocked stop, iteration cap) plus
the one that is the entire point: **evidence**. Every acceptance criterion must
link back to the interview, ticket, or usage datum that justifies it, and the
schema *refuses to compile* without it. This is not another spec format:
GitHub Spec Kit, AWS Kiro, and BMAD-METHOD already own those, and they're good.
A goal contract is the layer above them: intent with provenance, which compiles
*into* whatever your agent harness already reads.

**Manifesto (the why):** [[MANIFESTO-URL — Brett fills at publish time]]

## Quickstart

```bash
# 1. Copy the template
cp skill/contract-template.md my-feature.contract.md

# 2. Fill it in (frontmatter is canonical; every AC needs >=1 evidence entry)

# 3. Validate — stdlib-only Python, zero dependencies
python3 tools/validate.py my-feature.contract.md
```

Exit 0 = the contract compiles clean and is safe to hand to an agent. Exit 1 =
numbered errors telling you exactly what's missing.

**Don't want to write it by hand?** The Claude Code skill in `skill/` takes a
raw feature request plus evidence links and emits a valid contract, and it
refuses loudly when an AC has no evidence. See `skill/SKILL.md`.

## What's here

| Path | What it is |
|------|------------|
| `SCHEMA.md` | The v0.1 schema: seven fields, validation rules V1–V13, lifecycle semantics |
| `examples/BYE-282-dispatcher.contract.md` | A real contract, end to end, reconstructed from a production dispatch system |
| `skill/SKILL.md` + `skill/contract-template.md` | Claude Code skill: raw request + evidence → valid contract |
| `tools/validate.py` | Reference validator (Python 3.11+ stdlib only) |
| `manifesto.md` | The argument for all of this (pre-publication draft) |

## What's deliberately not here (yet)

No hosted pipeline, no integrations, no discovery-half features, no Spec Kit
preset or Kiro steering pack. Week 1 is the schema, one worked example, a
skill, and a validator. Files in, files out. The downstream pack ships when
measured pull says so.

## Status

v0.1, week 1 of a 90-day validation run. The schema was extracted from a
private agent-dispatch system that compiles and runs these contracts nightly;
the `evidence` field is the addition this repo exists to test.
