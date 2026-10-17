# Two-person delivery plan

## First milestone

A student enters completed courses, proposes a semester plan, sees specific
validation findings, and eventually saves an approved version. Start with one
catalog and two target careers. Career choice does not change academic rules.

Developer A and Developer B are provisional owners, not assigned people. Swap
them to suit your interests. Each person reviews the other's pull requests.

## Workstreams

| Area | Initial owner | Boundary | First deliverable |
| --- | --- | --- | --- |
| Contracts and product scope | Both | `src/planning/models.py`, `docs/` | Agree on request, response, and rule semantics |
| Academic data | A | catalog adapters and source snapshots | Versioned, reviewed course records |
| Planning and backend | A | `src/planning/`, future planning API | Deterministic validation, then authenticated persistence |
| Student experience | B | `frontend/src/` | Editable profile, proposed semesters, validation findings |
| Agent workflows | B, reviewed by A | future `src/workflows/` | Evidence retrieval, explanation, clarification and approval |
| Evaluation and delivery | Both | `tests/`, CI, deployment | Regression checks and repeatable local setup |

## Backlog in dependency order

Status is local to this document; these are not published GitHub issues.

| ID | Task | Owner | Depends on | Status | Acceptance criteria |
| --- | --- | --- | --- | --- | --- |
| F01 | Planning contracts and validation foundation | A | None | Done locally | Typed input/output, explicit unknown data, synthetic demo and rule regression tests |
| F02 | Agree on contract and example payload | Both | F01 | Ready | Both can explain prerequisites, term ordering and result statuses; changes reviewed together |
| D01 | Normalize catalog records | A | F02 | Ready after F02 | Preserve catalog version and source; unknown rules stay unknown; manually review representative records |
| U01 | Build profile and semester editor with fixtures | B | F02 | Ready after F02 | Enter completed courses and credit cap; edit semesters; render valid/blocked/needs-review examples |
| B01 | Authenticated profile storage | A | F02 | Backlog | Two users cannot read or modify each other's profiles; migrations and persistence across restart |
| B02 | Planning validation API | A | D01, B01 | Backlog | Server loads trusted catalog and profile; client supplies proposal only; returns documented findings |
| U02 | Connect editor to validation API | B | B02, U01 | Backlog | Invalid entries and request failures are actionable; previous proposal survives a failed request |
| A01 | Evidence-backed academic explanation | B | D01, B02 | Backlog | LangChain/model adapter behind an interface; every factual course claim references catalog evidence |
| A02 | Explicit planning workflow | B | A01 | Backlog | LangGraph clarification and approval pause; persistent checkpoints; retry-safe actions |
| B03 | Approve and version plans | A | B01, B02 | Backlog | Approval revalidates server-side; stale profile/catalog revisions detected; rejected checks cannot be bypassed |
| Q01 | Evaluate and pilot first vertical slice | Both | U02, A02, B03 | Backlog | Reviewed academic cases, cross-user tests, restart recovery, measured latency and inference cost |
| M01 | Market evidence and project milestones | Both | Q01 | Backlog | Licensed/permitted job sources, provenance, sample sizes, project rubrics and progress tracking |

F01 is a library foundation, not a running web feature or full academic planner.

## How to collaborate

Use one GitHub repository with both people as collaborators. Create a GitHub
Projects board: Backlog -> Ready -> In Progress -> Review -> Done. Copy the
backlog rows into issues when GitHub access is configured; assign one owner per
issue and link the implementation pull request. Do not maintain competing status
boards after that move.

For each task:

1. Agree on outcome and acceptance criteria; identify shared contract changes.
2. Create a branch such as `codex/f01-planning-contracts` from updated main.
3. Open a draft PR early; push checkpoints so your teammate can see progress.
4. Include the linked task, screenshots or example output, and verification.
5. The other developer reviews; passing relevant checks precede merging.

Keep one active implementation task per person initially. Post a short issue
comment when stopping: completed work, next step, blocker, branch/PR. Review
contracts together before changing both backend and frontend assumptions.

## Run the first foundation

From `evo-agents-main`, with Python 3.11+ and Pydantic 2 installed:

```powershell
python -m src.planning.demo
python -m unittest discover -s tests -v
python -m src.planning.demo --schema > docs/planning-request.schema.json
```

The demo needs no AWS credentials, browser automation, network or database. Its
courses are fictional fixtures, not verified UTD catalog data. Schema output is
generated from the Python models; do not hand-maintain a second JSON schema.

## Next session prompts

Developer A: "Implement D01 from docs/TEAM_PLAN.md after reviewing F02. Inspect
the existing catalog, propose normalization and preserve unknown prerequisites;
do not infer that missing text means no prerequisites."

Developer B: "Implement U01 from docs/TEAM_PLAN.md after reviewing F02. Use the
planning contract and clearly labeled fixtures; build profile/semester editing
and findings display before connecting a real API."
