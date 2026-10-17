"""Run a synthetic example, or export its request schema with --schema."""

import argparse
import json

from .models import PlanValidationRequest
from .validator import validate_plan


def sample_request() -> PlanValidationRequest:
    return PlanValidationRequest.model_validate({
        "catalog_version": "synthetic-demo-v1",
        "profile": {"completed_course_ids": ["DEMO101"], "max_credits_per_term": 6},
        "catalog": [
            {"course_id": "DEMO201", "credits": 3, "source_ref": "synthetic-fixture",
             "prerequisite_groups": [["DEMO101"]], "corequisite_groups": [],
             "offered_term_ids": ["2027-spring"]},
            {"course_id": "DEMO301", "credits": 3, "source_ref": "synthetic-fixture",
             "prerequisite_groups": [["DEMO201"]], "corequisite_groups": [],
             "offered_term_ids": ["2027-fall"]},
        ],
        "terms": [
            {"term_id": "2027-spring", "course_ids": ["DEMO201"]},
            {"term_id": "2027-fall", "course_ids": ["DEMO301"]},
        ],
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", action="store_true")
    parser.add_argument("--request", action="store_true", help="Print the synthetic request JSON")
    args = parser.parse_args()
    if args.schema:
        print(json.dumps(PlanValidationRequest.model_json_schema(), indent=2))
        return
    request = sample_request()
    if args.request:
        print(request.model_dump_json(indent=2))
        return
    print("SYNTHETIC DEMO: fictional courses, not UTD academic advice.")
    print(validate_plan(request).model_dump_json(indent=2))
    # Revalidate serialized input instead of bypassing the model validators.
    invalid = request.model_dump()
    invalid["terms"][0]["course_ids"] = ["DEMO301"]
    print("Blocked example: advanced course before its prerequisite.")
    print(validate_plan(PlanValidationRequest.model_validate(invalid)).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
