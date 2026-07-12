# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**csl-orig** is a Sanskrit Lexicon **data-store** repository — part of the Cologne Digital Sanskrit Lexicon (CDSL) infrastructure.

## Dictionary Correction Safety

`v02/<dict>/<dict>.txt` files are canonical dictionary sources. They may be
changed only through the documented CDSL correction workflow: snapshot, apply via
line-addressed change file or equivalent controlled edit, regenerate/validate,
create the `csl-corrections` audit trail, and commit the paired repos.

Before applying any old GitHub correction issue, search sibling `csl-corrections`
CFR and batch history for the same dictionary, L number, headword, old text, and
new text. If the registry says `No change`, rejected, deferred, or otherwise not
to be applied, **do not patch** unless a maintainer explicitly reopens the
decision.

For accepted corrections, decide before editing whether the source should use a
plain replacement or an inline correction layer such as
`{{old->new||YYYYMMDD|author|issue|}}`, which preserves the original reading.

## Repo Category

`data-store` — see the [tooling runbook](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md) for category-specific conventions.

## GitHub Issue Conventions

This repository uses the **Cologne tooling-repo taxonomy**. All issues must have:
- **Exactly one type label** (9 options)
- **Exactly one severity label** (4 levels)
- **One milestone** (5 options)

### Type Labels
- `bug` — Code defect (wrong output, broken contract)
- `feature` — Net-new capability
- `enhancement` — Improvement to existing capability
- `performance` — Speed, memory, throughput optimization
- `tech-debt` — Refactoring, cleanup, dependency updates
- `security` — CVE, auth issue, credential exposure
- `documentation` — Prose docs, API docs, comments
- `infrastructure` — CI/CD, deploy, data pipelines, build tooling
- `question` — Research, proposals, open discussions

### Severity Labels
- `trivial` — Cosmetic, < 1 hour
- `minor` — Single function/component
- `major` — Multiple files, design decision
- `critical` — Blocks users, data loss/security CVE

### Milestones
- **API Stability** — performance, security, regressions
- **User Experience** — bugs, features, enhancements
- **Data Quality** — data-pipeline issues, integrity
- **Developer Experience** — tech-debt, infrastructure, docs
- **Community** — questions, proposals, discussions

## Cross-Repo Coordination

The org-level project [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9) tracks tool work across all repositories.
