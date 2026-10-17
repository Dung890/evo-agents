import unittest

from pydantic import ValidationError

from src.planning.demo import sample_request
from src.planning.models import PlanValidationRequest
from src.planning.validator import validate_plan


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.data = sample_request().model_dump()

    def result(self):
        return validate_plan(PlanValidationRequest.model_validate(self.data))

    def codes(self):
        return {finding.code for finding in self.result().findings}

    def test_valid_sequential_plan(self):
        self.assertEqual(self.result().status, "valid")
        self.assertEqual(self.result().term_credits, {"2027-spring": 3, "2027-fall": 3})

    def test_same_term_cannot_satisfy_prerequisite(self):
        self.data["terms"] = [{"term_id": "2027-spring", "course_ids": ["DEMO201", "DEMO301"]}]
        self.assertIn("prerequisite_missing", self.codes())
        self.assertEqual(self.result().status, "blocked")

    def test_or_within_and_between_groups(self):
        self.data["catalog"][0]["prerequisite_groups"] = [["OTHER", "DEMO101"], ["SECOND"]]
        self.assertIn("prerequisite_missing", self.codes())
        self.data["profile"]["completed_course_ids"].append("SECOND")
        self.assertEqual(self.result().status, "valid")

    def test_corequisite_can_be_concurrent(self):
        self.data["catalog"][0]["corequisite_groups"] = [["DEMO301"]]
        self.data["catalog"][1]["prerequisite_groups"] = []
        self.data["catalog"][1]["offered_term_ids"] = ["2027-spring"]
        self.data["terms"] = [{"term_id": "2027-spring", "course_ids": ["DEMO201", "DEMO301"]}]
        self.assertEqual(self.result().status, "valid")

    def test_missing_corequisite(self):
        self.data["catalog"][0]["corequisite_groups"] = [["MISSING"]]
        self.assertIn("corequisite_missing", self.codes())

    def test_unknown_rules_and_offerings_require_review(self):
        self.data["catalog"][0]["prerequisite_groups"] = None
        self.data["catalog"][0]["offered_term_ids"] = None
        self.assertEqual(self.result().status, "needs_review")
        self.assertTrue({"unknown_requirements", "unknown_availability"} <= self.codes())

    def test_explicit_no_offerings_blocks(self):
        self.data["catalog"][0]["offered_term_ids"] = []
        self.assertIn("not_offered", self.codes())

    def test_unknown_course_blocks(self):
        self.data["terms"][0]["course_ids"] = ["MISSING"]
        self.assertIn("unknown_course", self.codes())

    def test_repeated_and_completed_courses_block(self):
        self.data["profile"]["completed_course_ids"].append("DEMO201")
        self.data["terms"][1]["course_ids"].append("DEMO201")
        self.assertTrue({"already_completed", "duplicate_course"} <= self.codes())

    def test_duplicate_within_term_not_double_counted(self):
        self.data["terms"][0]["course_ids"].append("DEMO201")
        self.assertIn("duplicate_course", self.codes())
        self.assertEqual(self.result().term_credits["2027-spring"], 3)

    def test_credit_cap(self):
        self.data["profile"]["max_credits_per_term"] = 2
        self.assertIn("credit_limit", self.codes())

    def test_invalid_contracts_rejected(self):
        for field, value in (("credits", 0), ("credits", True), ("course_id", " "), ("prerequisite_groups", [[]])):
            with self.subTest(field=field, value=value):
                data = sample_request().model_dump()
                data["catalog"][0][field] = value
                with self.assertRaises(ValidationError):
                    PlanValidationRequest.model_validate(data)

    def test_duplicate_catalog_and_term_ids_rejected(self):
        for key in ("catalog", "terms"):
            with self.subTest(key=key):
                data = sample_request().model_dump()
                data[key].append(data[key][0])
                with self.assertRaises(ValidationError):
                    PlanValidationRequest.model_validate(data)

    def test_errors_take_priority_over_review(self):
        self.data["catalog"][0]["offered_term_ids"] = None
        self.data["profile"]["max_credits_per_term"] = 2
        self.assertEqual(self.result().status, "blocked")


if __name__ == "__main__":
    unittest.main()
