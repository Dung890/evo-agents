#!/usr/bin/env python3
"""Offline audit of a collected snapshot; makes no network requests."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


class CourseTitleCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "span" and "course_title" in attributes.get("class", "").split():
            self.count += 1


def verify(root, year):
    checks = {}
    errors = []
    report = json.loads((root / f"catalog_report_{year}.json").read_text())
    records = [json.loads(line) for line in (root / f"courses_{year}.jsonl").read_text().splitlines() if line.strip()]
    sources = {}
    for sidecar in sorted((root / "raw" / "http").glob("*.json")):
        meta = json.loads(sidecar.read_text())
        path = root / meta["path"]
        data = path.read_bytes()
        if len(data) != meta["size_bytes"] or hashlib.sha256(data).hexdigest() != meta["sha256"]:
            errors.append(f"Source integrity mismatch: {path}")
        sources[meta["requested_url"]] = (meta, data)
    checks["http_response_files_checked"] = len(sources)
    counts = Counter((row["level"], row["prefix"]) for row in records)
    occurrences = Counter()
    for row in records:
        occurrences[(row["level"], row["prefix"])] += row["source_occurrences"]
        if not all(row.get(key) for key in ("id", "course_id", "title", "description_text", "course_url", "source_url", "retrieved_at")):
            errors.append(f"Missing required course field: {row.get('id')}")
        meta, _ = sources[row["source_url"]]
        if row["raw_source_path"] != meta["path"] or row["source_sha256"] != meta["sha256"]:
            errors.append(f"Course provenance mismatch: {row['id']}")
        expected_id = f"catalog:{year}:{row['level']}:{row['course_id'].lower()}"
        if row["id"] != expected_id or not row["course_url"].endswith("/" + row["course_id"].lower()):
            errors.append(f"Course identifier mismatch: {row['id']}")
    for page in report["pages"]:
        key = (page["level"], page["prefix"])
        if page["status"] not in ("ok", "empty"):
            errors.append(f"Failed catalog page: {page['source_url']}")
            continue
        if counts[key] != page["course_count"]:
            errors.append(f"Catalog page/export count mismatch: {page['source_url']}")
        _, raw = sources[page["source_url"]]
        counter = CourseTitleCounter()
        counter.feed(raw.decode("utf-8"))
        if counter.count != occurrences[key]:
            errors.append(f"Unaccounted source course entries: {page['source_url']}")
    checks["catalog_pages_checked"] = len(report["pages"])
    checks["course_records_checked"] = len(records)
    checks["source_course_entries_accounted_for"] = sum(occurrences.values())
    checks["unique_record_ids"] = len({row["id"] for row in records}) == len(records)
    checks["course_count_matches_report"] = len(records) == report["course_records"]
    checks["requested_pages_complete"] = report["complete_for_requested_prefix_pages"]
    checks["catalog_resume_network_requests"] = report["network_requests"]
    syllabi = [json.loads(line) for line in (root / "syllabi.jsonl").read_text().splitlines() if line.strip()]
    pdf_count = 0
    for row in syllabi:
        if row["status"] != "downloaded":
            errors.append(f"Syllabus not downloaded: {row['id']}")
            continue
        data = (root / row["pdf_path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != row["download"]["sha256"] or not data.startswith(b"%PDF-") or b"%%EOF" not in data[-4096:]:
            errors.append(f"Syllabus integrity mismatch: {row['id']}")
        pdf_count += 1
    checks["syllabus_pdfs_checked"] = pdf_count
    pdf_checks = json.loads((root / "pdf_validation.json").read_text()) if (root / "pdf_validation.json").exists() else []
    checks["pdfs_previously_opened_and_header_checked"] = sum(row["pages"] > 0 and row["sha256_matches"] and row["spring_2026_header_found"] and row["claimed_course_reference_found"] for row in pdf_checks)
    for key in ("unique_record_ids", "course_count_matches_report", "requested_pages_complete"):
        if not checks[key]:
            errors.append(f"Failed check: {key}")
    result = {"verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "passed": not errors, "checks": checks, "errors": errors}
    (root / "validation_report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--year", type=int, default=2026)
    args = parser.parse_args()
    sys.exit(verify(args.data, args.year))
