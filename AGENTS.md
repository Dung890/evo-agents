# Shared development guidance

## Project context

Read `docs/TEAM_PLAN.md` for scope, workstreams and task acceptance criteria.
Read `docs/PLANNING_CONTRACT.md` before changing planning models or rules.
The existing application is a legacy prototype; `src/planning/` is an isolated
foundation for its product revamp. Do not describe this foundation as integrated
or production-ready until the corresponding work has been completed.

## Collaboration

- Implement one agreed task per branch and keep changes focused.
- Record durable decisions in docs and task/PR descriptions, not only chat.
- Update the shared contract and examples together when behavior changes.
- Use the GitHub issue board for live status once it exists; local backlog rows
  are initial planning aids, not evidence that GitHub issues were created.

## Data and AI boundaries

- Label synthetic fixtures explicitly. Preserve provenance and catalog versions.
- Missing prerequisites or offerings are unknown, not evidence of no rules.
- Academic feasibility and authorization are server-side deterministic checks.
- Model outputs cannot approve plans, assign user identity or override checks.
- Keep library imports independent of AWS credentials and browser automation.
- Do not include credentials, personal documents or local sessions in commits.

## Verification

From this directory, run `python -m unittest discover -s tests -v` for planning
changes and `python -m src.planning.demo` for its example flow. Run relevant
frontend checks for UI changes. State what was tested and any remaining limits.
