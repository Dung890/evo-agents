"""Shared contract for validation of a proposed plan against a supplied catalog.

The future API must obtain the catalog and confirmed profile server-side.
This library input is not a public API authorization boundary.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^\S+(?:.*\S)?$")]
CourseIds = Annotated[list[Identifier], Field(max_length=500)]
PrerequisiteGroup = Annotated[list[Identifier], Field(min_length=1, max_length=50)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class StudentProfile(Contract):
    completed_course_ids: CourseIds = Field(default_factory=list)
    max_credits_per_term: Annotated[int, Field(ge=1, le=30)] = 15


class CourseRecord(Contract):
    course_id: Identifier
    credits: Annotated[int, Field(ge=1, le=30)]
    source_ref: Identifier
    # Every group is required; any one course in a group satisfies that group.
    # None = unknown; [] = verified absence of requirements.
    prerequisite_groups: list[PrerequisiteGroup] | None = None
    corequisite_groups: list[PrerequisiteGroup] | None = None
    # Exact term IDs, not inferred recurrence. None = unknown; [] = no offerings.
    offered_term_ids: CourseIds | None = None


class ProposedTerm(Contract):
    term_id: Identifier
    course_ids: Annotated[list[Identifier], Field(min_length=1, max_length=50)]


class PlanValidationRequest(Contract):
    catalog_version: Identifier
    profile: StudentProfile
    catalog: Annotated[list[CourseRecord], Field(min_length=1, max_length=10000)]
    # The caller supplies chronological order; term IDs are opaque identifiers.
    terms: Annotated[list[ProposedTerm], Field(min_length=1, max_length=30)]

    @model_validator(mode="after")
    def unique_records(self):
        ids = [course.course_id for course in self.catalog]
        if len(ids) != len(set(ids)):
            raise ValueError("Catalog course IDs must be unique")
        term_ids = [term.term_id for term in self.terms]
        if len(term_ids) != len(set(term_ids)):
            raise ValueError("Term IDs must be unique and supplied chronologically")
        return self


class Finding(Contract):
    code: Literal[
        "unknown_course", "duplicate_course", "already_completed",
        "credit_limit", "prerequisite_missing", "corequisite_missing",
        "not_offered", "unknown_requirements", "unknown_availability",
    ]
    severity: Literal["error", "review"]
    term_id: Identifier
    course_id: Identifier | None = None
    message: str


class PlanValidationResult(Contract):
    schema_version: Literal["1"] = "1"
    catalog_version: Identifier
    status: Literal["valid", "blocked", "needs_review"]
    findings: list[Finding]
    term_credits: dict[str, int]
