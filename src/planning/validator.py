"""Validate represented rules; do not infer missing academic requirements."""

from .models import Finding, PlanValidationRequest, PlanValidationResult


def validate_plan(request: PlanValidationRequest) -> PlanValidationResult:
    catalog = {course.course_id: course for course in request.catalog}
    completed = set(request.profile.completed_course_ids)
    earlier = set(completed)
    seen: set[str] = set()
    findings: list[Finding] = []
    term_credits: dict[str, int] = {}

    for term in request.terms:
        current = set(term.course_ids)

        def report(code, severity, message, course_id=None):
            findings.append(Finding(
                code=code, severity=severity, term_id=term.term_id,
                course_id=course_id, message=message,
            ))

        credits = 0
        for course_id in term.course_ids:
            if course_id in seen:
                report("duplicate_course", "error", "Course appears more than once in the plan.", course_id)
                continue
            seen.add(course_id)
            if course_id in completed:
                report("already_completed", "error", "Course is already completed; repeat-credit rules are not supported.", course_id)

            course = catalog.get(course_id)
            if course is None:
                report("unknown_course", "error", "Course is absent from the selected catalog.", course_id)
                continue
            credits += course.credits

            for groups, eligible, code, label in (
                (course.prerequisite_groups, earlier, "prerequisite_missing", "prerequisite"),
                (course.corequisite_groups, earlier | current, "corequisite_missing", "corequisite"),
            ):
                if groups is None:
                    report("unknown_requirements", "review", f"Verified {label} rules are unavailable.", course_id)
                else:
                    for alternatives in groups:
                        if not eligible.intersection(alternatives):
                            report(code, "error", f"Unsatisfied {label}: one of {', '.join(alternatives)} is required.", course_id)

            if course.offered_term_ids is None:
                report("unknown_availability", "review", "Term availability has not been verified.", course_id)
            elif term.term_id not in course.offered_term_ids:
                report("not_offered", "error", "Course is not offered in this term according to the supplied record.", course_id)

        term_credits[term.term_id] = credits
        if credits > request.profile.max_credits_per_term:
            report("credit_limit", "error", f"{credits} known credits exceeds the {request.profile.max_credits_per_term}-credit limit.")
        # Earlier proposed courses count as assumed completions in later terms.
        # Any failure still blocks the entire proposal; no approval occurs here.
        earlier.update(current.intersection(catalog))

    status = "valid"
    if any(f.severity == "error" for f in findings):
        status = "blocked"
    elif findings:
        status = "needs_review"
    return PlanValidationResult(
        catalog_version=request.catalog_version, status=status,
        findings=findings, term_credits=term_credits,
    )
