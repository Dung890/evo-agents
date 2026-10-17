# Included snapshot: UTD 2026 course source data

Collected and verified on October 17, 2026. This snapshot preserves source material for a later topic extraction step.

| Dataset | Coverage |
| --- | --- |
| Undergraduate catalog | 2,609 course descriptions across 105 listed prefix pages |
| Graduate catalog | 2,513 course descriptions across 79 listed prefix pages |
| Total | 5,122 distinct course records and course identifiers |
| Catalog page outcomes | 184 successfully parsed; 0 failed; 3 genuinely empty |
| Public syllabus pilot | 7 original PDFs from Spring 2026; 52 pages total |

## Start with these files

- `data/courses_2026.jsonl`: course identifiers, names, credit hours, full descriptions, school/prefix/level, course URLs, and source provenance.
- `data/syllabi.jsonl` and `data/syllabi/`: syllabus inventory and original PDF files.
- `data/raw/http/`: original source HTML/PDF bodies and response metadata.
- `data/catalog_report_2026.json`, `data/syllabus_report.json`, and `data/validation_report.json`: scope, outcomes, and verification evidence.
- `collector.py`, `verify_data.py`, `tests/`, and `README.md`: reusable code, checks, and commands.

## Catalog coverage and source quirks

Every prefix linked by the official 2026 undergraduate and graduate course-prefix indexes was requested. The empty pages are: graduate AHTC; undergraduate CPSY; undergraduate HIND.

The source contains 5,123 course paragraph occurrences. One identical MIS 6388 duplicate was merged, preserving both source HTML anchors and the occurrence count. The resulting dataset has 5,122 unique course records, with no empty descriptions or duplicate stable identifiers. The MIS 6388 source had an incorrect extra HTML anchor, and MECH 6314 had nested source markup; both discrepancies are preserved in `source_warnings`.

Descriptions retain prerequisites, restrictions, and published notes. Course catalog membership does not establish that the course is offered in Fall 2026 or another particular term. Special topics and independent-study descriptions may remain generic; a specific offering's syllabus is needed for its actual teaching plan.

## Syllabus sample and remaining coverage gap

The seven included syllabi are explicitly a small development sample from **Spring 2026**, not Fall 2026 and not a university-wide census. They cover CS 1337, CS 3345, CS/CE 4337, CS 4390, MATH 2413, OPRE 3360, and PHYS 2325. Course/term labels came from indexed official document headers and were checked against the downloaded PDF text. Unknown section lists remain unspecified; some PDFs are shared across sections.

The current CourseBook search URL observed in the site's JavaScript redirected to UTD's NetID login, and an anonymous guest guided-search request returned HTTP 404. Full section-level syllabus discovery was therefore not completed. Public syllabus URLs or an authorized export are the next input needed for broader semester coverage. See `data/access_status.json` for the tested routes.

## Verification performed

- 13 offline regression tests passed.
- All 193 saved HTTP response bodies matched their recorded SHA-256 and byte counts.
- All 184 requested catalog prefix pages were accounted for; independent source-tag counts matched all 5,123 source occurrences.
- All 5,122 records had stable unique IDs, nonempty titles and descriptions, and matching raw-source provenance.
- All 7 original PDFs opened with a PDF reader, had the expected course/Spring 2026 context in their headers, and matched their recorded hashes.
- A complete catalog rerun used 186 cached responses (184 prefix pages plus two indexes) and made 0 network requests.
- A syllabus rerun used 7 cached PDFs and made 0 network requests.

No topic extraction, weekly schedule parsing, embeddings, or inferred subject labels have been performed.

## Primary sources

- https://catalog.utdallas.edu/2026/undergraduate/courses
- https://catalog.utdallas.edu/2026/graduate/courses
- Individual official UTD PDF URLs in `examples/public_syllabi.jsonl`.
- Original repository reviewed as a reference: https://github.com/aemmadi/coursebook-api
