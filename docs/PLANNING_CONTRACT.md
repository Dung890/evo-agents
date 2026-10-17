# Planning contract v1

Source of truth: `src/planning/models.py`. Export request JSON with
`python -m src.planning.demo --request` and schema with `--schema`. Response
schema is available from `PlanValidationResult.model_json_schema()`.

## Semantics

- Course and term IDs are exact, canonical, case-sensitive identifiers. A future
  catalog adapter must normalize source identifiers before calling this library.
- Input terms must be chronological. This first contract does not parse term
  names or verify their chronology; the future API must construct ordered terms.
- Prerequisites must be completed before a term starts. A course in the same
  term cannot satisfy a prerequisite. Earlier proposed courses are assumed to
  be successfully completed, conditional on the whole proposal being feasible.
- Every prerequisite group must be satisfied. Within a group, any alternative
  suffices. `[["A", "B"], ["C"]]` means `(A OR B) AND C`.
- Corequisites may be completed earlier or taken in the same term.
- `null` prerequisite/corequisite groups means unknown. `[]` means a reviewed
  source establishes that there are no requirements of that kind.
- `null` offerings means unknown. `[]` means no verified offerings in the
  supplied planning horizon. Exact term IDs must match.
- Catalog version and source references are provided by a trusted adapter.
  The library preserves their identifiers but does not verify the sources.
- Credit totals count unique known scheduled courses. Unknown/duplicate course
  findings block a plan; totals are not an authoritative workload in that case.

## Results

`blocked`: at least one represented rule failed. `needs_review`: no rule failed
but requirements or availability are unknown. `valid`: supplied rules passed.
None of these statuses constitutes approval, enrollment eligibility or degree
completion. Approval will require authenticated, server-side revalidation.

This first slice does not implement minimum grades, standing, placement tests,
permissions, degree audits, transfer equivalencies, variable/repeat credits,
time conflicts, source freshness, automatic scheduling, persistence or agents.
Catalog adaptation must mark unrepresented requirements as unknown rather than
discard them. Until that adapter exists, only synthetic fixtures are supported.

## Future API boundary

Do not expose this entire request as a trusted public endpoint: a browser could
replace prerequisites with empty arrays. The future API accepts a proposed plan
and profile revision, then loads the user's confirmed profile and authoritative
catalog server-side. It enforces ownership, checks revisions, validates again,
and only then records approval.
