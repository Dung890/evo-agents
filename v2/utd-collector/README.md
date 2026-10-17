# UTD course source data collector

Collects published course descriptions from the official UT Dallas catalogs and downloads public syllabus PDFs from an explicit URL inventory. The collector saves source documents and provenance for later topic extraction. It does not infer topics or scrape authenticated pages.

See `SNAPSHOT.md` for the included collection's exact scope, counts, and remaining gaps.

## Run it

Requires Python 3.10 or newer and `lxml`. No browser, ChromeDriver, Flask server, or MongoDB is needed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# All prefixes listed by the 2026 undergraduate and graduate catalogs.
python collector.py catalog --year 2026 --output data

# The included public syllabus sample. This is a Spring 2026 sample.
python collector.py syllabi \
  --manifest examples/public_syllabi.jsonl --output data
```

On Windows, activate the environment with `.venv\Scripts\activate`.

For a small development run, use a separate directory so you retain the full dataset:

```bash
python collector.py catalog --year 2026 --prefixes CS SE \
  --levels undergraduate graduate --output data_cs_se
```

Each catalog invocation exports exactly the requested scope to `courses_YEAR.jsonl` and its reports. A different prefix filter in the same output directory replaces those exports. Raw download checkpoints remain reusable.

## Included data and file formats

| Path | Contents |
| --- | --- |
| `data/courses_2026.jsonl` | One JSON object per course and catalog level. |
| `data/prefixes_2026.json` | Every discovered prefix, its name, school, level, and source URL. |
| `data/catalog_report_2026.json` | Requested scope, counts, per-prefix outcomes, and completeness of the requested catalog pages. |
| `data/syllabi.jsonl` | Syllabus inventory, supplied course/term labels, download outcomes, hashes, and file paths. |
| `data/syllabi/*.pdf` | Original, unmodified downloaded syllabus PDFs. |
| `data/syllabus_report.json` | Coverage and download counts for the supplied syllabus inventory. |
| `data/raw/http/*` | Original HTTP bodies and JSON sidecars recording source URL, retrieval time, content type, byte count, and SHA-256. |
| `data/*progress*.json` | Checkpoints showing finished requests and failures. |

`courses_2026.jsonl` includes `course_id`, `course_number`, `title`, `credit_hours_text`, `description_text`, `full_text`, `catalog_year`, `level`, `prefix`, `prefix_name`, `school`, course/source URLs, and source-file provenance. Variable-credit codes such as `CS2V95` are retained. Equivalent course references are recorded separately.

Source HTML discrepancies are retained in `source_warnings` and `source_html_anchors`. An incorrect HTML anchor does not override the displayed course link. Identical duplicate entries are merged with `source_occurrences` recording the original count; conflicting duplicate entries fail validation.

Descriptions retain prerequisites, restrictions, offering notes, cross-listing notes, and other text published in the course paragraph. They are source text, not extracted topic lists. A catalog entry does not establish that the course is offered in a particular semester. A shared or cross-listed syllabus may cover several course identifiers or sections.

## Add syllabus documents

Create a UTF-8 JSONL file with one inventory record per line. Each record requires a stable, unique `id`; the remaining descriptive metadata is retained as supplied:

```json
{"id":"dox:syl162945","syllabus_url":"https://dox.utdallas.edu/syl162945","course_ids":["CS1337"],"term":"26s","course_sections":[]}
```

Then run:

```bash
python collector.py syllabi --manifest my_syllabus_inventory.jsonl --output data
```

Inventory URLs should come from public links or an authorized CourseBook export. Do not guess document IDs or supply credentials. A missing URL is recorded as `missing_url`; it does not establish that no syllabus exists. An absent term/section should remain unknown. PDF course/semester labels are input metadata rather than automatic content extraction.

The included sample's labels were taken from the indexed headers of official public PDFs. It is a small convenience sample, not a complete or representative syllabus census. The collection's validation report separately checks that those PDFs open and match the claimed Spring 2026 context.

## Resume, refresh, and failures

- Rerun the same command to reuse valid saved responses and retry missing or failed requests. Reuse preserves the original retrieval time and verifies the saved SHA-256. No special `--resume` flag is required.
- Use `--refresh` to fetch a new snapshot of requested sources. To retain multiple snapshots, select a new output directory.
- The default is three workers with at least one second between network requests globally. `--workers` accepts 1–4; `--delay` has a minimum of 0.5 seconds.
- Transient timeouts, HTTP 429, and selected HTTP 5xx responses are retried. A long numeric `Retry-After` stops that request so a later rerun can continue.
- Empty responses, recognized login pages, non-PDF downloads, and PDFs without an end marker are rejected. A PDF download is capped at 30 MiB. Only public HTTPS UTD URLs are accepted; sign-in redirects stop the request.
- Parser changes and failed pages appear in the report and produce exit code 2. Successfully fetched, genuinely empty prefix pages are explicitly marked `empty` and counted separately.
- Completeness means every requested prefix page was parsed. It is not a guarantee that the university's own catalog is exhaustive or that all semester syllabi have been acquired.

The included catalog sources were read from the public 2026 catalog paths. Both sites' published `robots.txt` files were checked before collection. The included run did not request generated print/export endpoints or future catalog paths.

## CourseBook limitation

The reviewed repository, <https://github.com/aemmadi/coursebook-api>, supplied the initial reference for the CourseBook fields. Its legacy detail endpoint returned empty responses during live checks. The current search route observed in CourseBook's own JavaScript redirected to UTD's Comet Auth / NetID login, and the guest guided-search request returned HTTP 404.

Consequently this collector uses accessible official catalogs for the course inventory and descriptions, and known public PDF links for the syllabus pilot. Automatic discovery of all current section-level syllabi is **not implemented or claimed**. An authorized export with course, term, section, and syllabus URLs is the next input needed to expand that coverage. No credentials or captured authenticated sessions are included.

## Verification

```bash
python -m unittest discover -s tests -v
python verify_data.py --data data --year 2026
```

Offline tests cover preservation of nested description text, variable-credit and equivalent course identifiers, navigation filtering, genuine empty pages versus changed markup, duplicate records, invalid downloads, authentication redirects, corrupted checkpoints, and resume without network access.

The offline snapshot audit checks every saved HTTP response hash and byte count, each course's provenance and stable identifier, source-entry counts using a separate standard-library HTML parser, and the downloaded PDF hashes and end markers. The included `pdf_validation.json` also records the one-time PDF open and header checks; that earlier semantic check is not rerun by `verify_data.py`.

`SNAPSHOT.md` and `data/validation_report.json` describe the checks actually performed on the included live collection. Topic extraction, topic normalization, embeddings, and weekly schedule parsing are intentionally deferred.
