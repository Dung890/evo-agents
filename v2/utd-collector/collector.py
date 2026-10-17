#!/usr/bin/env python3
"""Collect public UTD course source data; deliberately does not infer topics."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from lxml import html

LOG = logging.getLogger("utd_collector")
VERSION = "0.1.0"
CATALOG = "https://catalog.utdallas.edu"
COURSEBOOK = "https://coursebook.utdallas.edu"
UA = "UTDCourseCollector/0.1 (public academic course-data collection)"


class CollectionError(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(text):
    return " ".join(text.split())


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def write_jsonl(path, records):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    temporary.replace(path)


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or parts.username or parts.password:
        raise CollectionError("Only public HTTPS URLs without embedded credentials are supported")
    if host != "utdallas.edu" and not host.endswith(".utdallas.edu"):
        raise CollectionError(f"Unexpected download host: {host}")
    if "/login" in parts.path.lower():
        raise CollectionError("UTD sign-in is required; no credentials or login bypass are supported")


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        check_url(new_url)
        return super().redirect_request(request, response, code, message, headers, new_url)


class HttpStore:
    """Rate limited downloads with validated, content-hashed disk checkpoints."""

    def __init__(self, root, delay=1.0, timeout=30, retries=2, refresh=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.refresh = refresh
        self.lock = threading.Lock()
        self.last_request = 0.0
        self.local = threading.local()
        self.network_requests = 0
        self.cache_hits = 0

    def wait(self):
        with self.lock:
            remaining = self.delay - (time.monotonic() - self.last_request)
            if remaining > 0:
                time.sleep(remaining)
            self.last_request = time.monotonic()

    @staticmethod
    def validate(data, kind):
        if not data:
            raise CollectionError("Empty response; not accepted as a collected document")
        if kind == "pdf":
            if not data[:1024].lstrip().startswith(b"%PDF-"):
                raise CollectionError("Expected a PDF; received another document, possibly an access page")
            if b"%%EOF" not in data[-4096:]:
                raise CollectionError("PDF has no end-of-file marker; the download may be truncated")
            return
        if kind == "html":
            head = data[:20000].lower()
            if (b"comet auth" in head and b"login-form" in data.lower()) or b"you must be signed in to view this page" in head:
                raise CollectionError("UTD sign-in is required; received a login page")
            if b"<html" not in head and b"<div" not in head and b"<p" not in head and b"<table" not in head:
                raise CollectionError("Expected HTML; received an unrecognized response")

    def save_response(self, url, data, kind="html", final_url=None, content_type="text/html", retrieved_at=None, method="GET", form=None):
        check_url(url)
        check_url(final_url or url)
        self.validate(data, kind)
        key = self.key(url, method, form)
        relative = Path("raw") / "http" / f"{key}.{kind}"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
        metadata = {
            "requested_url": url, "final_url": final_url or url,
            "method": method, "form": form,
            "retrieved_at": retrieved_at or now(), "http_status": 200,
            "content_type": content_type, "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data), "path": relative.as_posix(),
        }
        atomic_json(self.root / "raw" / "http" / f"{key}.json", metadata)
        return data, metadata

    @staticmethod
    def key(url, method="GET", form=None):
        identity = json.dumps([method, url, form], sort_keys=True)
        return hashlib.sha256(identity.encode()).hexdigest()

    def fetch(self, url, kind="html", method="GET", form=None):
        check_url(url)
        key = self.key(url, method, form)
        checkpoint = self.root / "raw" / "http" / f"{key}.json"
        if checkpoint.exists() and not self.refresh:
            try:
                meta = json.loads(checkpoint.read_text())
                data = (self.root / meta["path"]).read_bytes()
                self.validate(data, kind)
                if hashlib.sha256(data).hexdigest() == meta["sha256"]:
                    with self.lock:
                        self.cache_hits += 1
                    return data, meta
            except (OSError, KeyError, ValueError, CollectionError):
                pass
        error = None
        for attempt in range(self.retries + 1):
            self.wait()
            try:
                if not hasattr(self.local, "opener"):
                    self.local.opener = urllib.request.build_opener(PublicRedirect())
                payload = urllib.parse.urlencode(form, doseq=True).encode() if form is not None else None
                request = urllib.request.Request(url, data=payload, method=method, headers={"User-Agent": UA})
                with self.lock:
                    self.network_requests += 1
                with self.local.opener.open(request, timeout=self.timeout) as response:
                    check_url(response.url)
                    data = response.read(30 * 1024 * 1024 + 1)
                    if len(data) > 30 * 1024 * 1024:
                        raise CollectionError("Document exceeds the 30 MiB download limit")
                    return self.save_response(url, data, kind, response.url, response.headers.get("Content-Type", ""), method=method, form=form)
            except urllib.error.HTTPError as exc:
                error = f"HTTP {exc.code} for {url}"
                if exc.code not in (408, 429, 500, 502, 503, 504):
                    break
                retry_after = exc.headers.get("Retry-After", "")
                pause = max(2 ** (attempt + 1), int(retry_after) if retry_after.isdigit() else 0)
                if pause > 60:
                    raise CollectionError(f"Server requested a long pause ({pause}s); rerun later") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                error = f"{type(exc).__name__}: {exc}"
                pause = 2 ** (attempt + 1)
            if attempt < self.retries:
                time.sleep(pause)
        raise CollectionError(error or f"Could not retrieve {url}")


def classes(name):
    return f'contains(concat(" ", normalize-space(@class), " "), " {name} ")'


def content_after(root, marker):
    """Read text after credits even when the publisher left a span unclosed."""
    found = False
    text = []
    before_links = []
    after_links = []

    def walk(node):
        nonlocal found
        if node is marker:
            found = True
            return
        if node.tag == "a" and node.get("href"):
            (after_links if found else before_links).append(node)
        if found and node.text:
            text.append(node.text)
        for child in node:
            walk(child)
            if found and child.tail:
                text.append(child.tail)

    walk(root)
    return clean("".join(text)), before_links, after_links


def parse_prefixes(data, year, level):
    tree = html.fromstring(data)
    pattern = re.compile(rf"/{year}/{level}/courses/([a-z]+)$")
    prefixes = {}
    for row in tree.xpath('//*[@id="bukku-page"]//tr'):
        cells = row.xpath("./td")
        if len(cells) < 3:
            continue
        for link in cells[0].xpath(".//a[@href]"):
            match = pattern.search(link.get("href"))
            if match:
                prefix = match.group(1)
                prefixes[prefix] = {
                    "prefix": prefix.upper(), "prefix_name": clean(cells[1].text_content()),
                    "school": clean(cells[2].text_content()),
                    "url": urllib.parse.urljoin(CATALOG, link.get("href")),
                    "catalog_year": year, "level": level,
                }
    if not prefixes:
        raise CollectionError(f"No prefixes found in the {year} {level} index; inspect source markup/access")
    return [prefixes[key] for key in sorted(prefixes)]


def parse_catalog(data, prefix, metadata):
    tree = html.fromstring(data)
    records = {}
    titles = tree.xpath(f'//*[@id="bukku-page"]//span[{classes("course_title")}]')
    if not titles:
        containers = tree.xpath('//*[@id="bukku-page"]')
        if containers:
            children = list(containers[0])
            if (len(children) == 1 and children[0].tag == "h1"
                    and clean(children[0].text_content()) == prefix["prefix_name"]
                    and clean(containers[0].text_content()) == prefix["prefix_name"]):
                # Some official prefix pages intentionally contain only a heading.
                return []
        raise CollectionError(f"No course descriptions found for {prefix['url']}; inspect saved source")
    for title in titles:
        paragraphs = title.xpath("ancestor::p[1]")
        if not paragraphs:
            raise CollectionError("Course markup changed: no enclosing course paragraph")
        paragraph = paragraphs[0]
        addresses = paragraph.xpath(f'.//span[{classes("course_address")}]//a[@href]')
        hours = paragraph.xpath(f'.//span[{classes("course_hours")}]')
        if not addresses or len(hours) != 1:
            raise CollectionError("Course markup changed: missing address or ambiguous credit hours")
        # The catalog contains at least one incorrect HTML anchor. Use the
        # actual course link and displayed code, retaining source discrepancies.
        course_url = urllib.parse.urljoin(prefix["url"], addresses[0].get("href"))
        code = urllib.parse.urlsplit(course_url).path.rstrip("/").split("/")[-1].upper()
        if not re.fullmatch(re.escape(prefix["prefix"]) + r"[0-9][A-Z0-9]*", code):
            raise CollectionError(f"Unexpected course identifier {code!r}")
        display_code = re.sub(r"\s+", "", addresses[0].text_content()).upper()
        if display_code != code:
            raise CollectionError(f"Course link/display mismatch: {code!r} versus {display_code!r}")
        description, header_links, description_links = content_after(paragraph, hours[0])
        if not description:
            raise CollectionError(f"Empty description for {code}")
        warnings = []
        source_anchor = paragraph.get("id")
        if source_anchor and source_anchor.upper() != code:
            warnings.append("source_html_anchor_differs_from_course_code")
        if title.getparent() is not paragraph:
            warnings.append("source_course_title_has_nested_markup")
        record_id = f"catalog:{prefix['catalog_year']}:{prefix['level']}:{code.lower()}"
        record = {
            "id": record_id, "course_id": code,
            "course_number": code[len(prefix["prefix"]):],
            "course_code_display": clean(addresses[0].text_content()),
            "title": clean(title.text_content()), "credit_hours_text": clean(hours[0].text_content()),
            "description_text": description, "full_text": clean(paragraph.text_content()),
            "equivalent_course_references": [clean(link.text_content()) for link in header_links if link is not addresses[0]],
            "referenced_course_urls": sorted({urllib.parse.urljoin(prefix["url"], a.get("href")) for a in description_links if "/courses/" in a.get("href")}),
            "catalog_year": prefix["catalog_year"], "level": prefix["level"],
            "prefix": prefix["prefix"], "prefix_name": prefix["prefix_name"], "school": prefix["school"],
            "source_type": "official_catalog", "source_url": prefix["url"],
            "course_url": course_url, "source_html_anchor": source_anchor,
            "source_html_anchors": [source_anchor] if source_anchor else [],
            "source_occurrences": 1, "source_warnings": warnings,
            "raw_source_path": metadata["path"], "source_sha256": metadata["sha256"],
            "retrieved_at": metadata["retrieved_at"],
        }
        if record_id in records:
            existing = records[record_id]
            provenance_fields = {"source_html_anchor", "source_html_anchors", "source_occurrences", "source_warnings"}
            if ({k: v for k, v in existing.items() if k not in provenance_fields}
                    != {k: v for k, v in record.items() if k not in provenance_fields}):
                raise CollectionError(f"Conflicting duplicate course in one prefix page: {record_id}")
            existing["source_occurrences"] += 1
            existing["source_html_anchors"] = sorted(set(existing["source_html_anchors"] + record["source_html_anchors"]))
            existing["source_warnings"] = sorted(set(existing["source_warnings"] + warnings + ["identical_duplicate_in_source_page"]))
        else:
            records[record_id] = record
    return list(records.values())


def collect_catalog(args):
    root = args.output
    client = HttpStore(root, args.delay, args.timeout, args.retries, args.refresh)
    prefixes = []
    for level in args.levels:
        url = f"{CATALOG}/{args.year}/{level}/courses"
        data, _ = client.fetch(url)
        discovered = parse_prefixes(data, args.year, level)
        if args.prefixes:
            wanted = set(args.prefixes)
            discovered = [item for item in discovered if item["prefix"] in wanted]
        prefixes.extend(discovered)
    if not prefixes:
        raise CollectionError("No prefixes match the requested scope")
    prefix_path = root / f"prefixes_{args.year}.json"
    atomic_json(prefix_path, prefixes)
    records = []
    states = []

    def collect_one(prefix):
        data, metadata = client.fetch(prefix["url"])
        return parse_catalog(data, prefix, metadata)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        tasks = {pool.submit(collect_one, prefix): prefix for prefix in prefixes}
        for future in as_completed(tasks):
            prefix = tasks[future]
            state = {"level": prefix["level"], "prefix": prefix["prefix"], "source_url": prefix["url"]}
            try:
                rows = future.result()
                records.extend(rows)
                state.update(status="ok" if rows else "empty", course_count=len(rows))
                LOG.info("%s %s: %d courses (%d/%d pages)", prefix["level"], prefix["prefix"], len(rows), len(states) + 1, len(prefixes))
            except Exception as exc:
                state.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                LOG.error("%s %s: %s", prefix["level"], prefix["prefix"], exc)
            states.append(state)
            atomic_json(root / f"catalog_progress_{args.year}.json", {"updated_at": now(), "requested_pages": len(prefixes), "finished_pages": len(states), "pages": sorted(states, key=lambda item: (item["level"], item["prefix"]))})
    records.sort(key=lambda record: record["id"])
    if len({record["id"] for record in records}) != len(records):
        raise CollectionError("Duplicate IDs across prefix pages; refusing to publish an ambiguous dataset")
    output = root / f"courses_{args.year}.jsonl"
    # Export exactly this run's requested scope. Raw checkpoints remain reusable.
    write_jsonl(output, records)
    report = {
        "collector_version": VERSION, "finished_at": now(), "catalog_year": args.year,
        "levels": args.levels, "requested_prefix_filter": args.prefixes,
        "requested_prefix_pages": len(prefixes), "successful_prefix_pages": sum(s["status"] in ("ok", "empty") for s in states),
        "empty_prefix_pages": sum(s["status"] == "empty" for s in states),
        "failed_prefix_pages": sum(s["status"] == "failed" for s in states),
        "course_records": len(records), "unique_course_ids": len({r["course_id"] for r in records}),
        "source_course_occurrences": sum(r["source_occurrences"] for r in records),
        "identical_source_duplicates_merged": sum(r["source_occurrences"] - 1 for r in records),
        "course_records_with_source_warnings": sum(bool(r["source_warnings"]) for r in records),
        "courses_by_level": {level: sum(r["level"] == level for r in records) for level in args.levels},
        "output": output.name, "network_requests": client.network_requests, "cache_hits": client.cache_hits,
        "complete_for_requested_prefix_pages": all(s["status"] in ("ok", "empty") for s in states),
        "scope_note": "Catalog descriptions, including prerequisites/notes as published. Catalog inclusion does not establish that a course is offered in a particular semester. Syllabi and inferred topics are separate datasets.",
        "pages": sorted(states, key=lambda state: (state["level"], state["prefix"])),
    }
    atomic_json(root / f"catalog_report_{args.year}.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "pages"}, indent=2))
    return 0 if report["complete_for_requested_prefix_pages"] else 2


def load_manifest(path):
    records = []
    identities = set()
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise CollectionError(f"Manifest line {line_number} needs a nonempty string id")
        if row["id"] in identities:
            raise CollectionError(f"Duplicate manifest id: {row['id']}")
        identities.add(row["id"])
        url = row.get("syllabus_url")
        if url is not None and not isinstance(url, str):
            raise CollectionError(f"Manifest line {line_number} has a non-string syllabus URL")
        if url:
            check_url(url)
        records.append(row)
    if not records:
        raise CollectionError("The syllabus manifest is empty")
    return records


def collect_syllabi(args):
    root = args.output
    rows = load_manifest(args.manifest)
    client = HttpStore(root, args.delay, args.timeout, args.retries, args.refresh)
    urls = sorted({row["syllabus_url"] for row in rows if row.get("syllabus_url")})
    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        tasks = {pool.submit(client.fetch, url, "pdf"): url for url in urls}
        for future in as_completed(tasks):
            url = tasks[future]
            try:
                data, metadata = future.result()
                document_name = urllib.parse.urlsplit(url).path.rstrip("/").split("/")[-1]
                if not re.fullmatch(r"syl[0-9]+", document_name):
                    document_name = hashlib.sha256(url.encode()).hexdigest()[:24]
                pdf_path = Path("syllabi") / f"{document_name}.pdf"
                (root / pdf_path).parent.mkdir(parents=True, exist_ok=True)
                temporary = (root / pdf_path).with_suffix(".pdf.tmp")
                temporary.write_bytes(data)
                temporary.replace(root / pdf_path)
                results[url] = {"status": "downloaded", "pdf_path": pdf_path.as_posix(), "download": metadata}
                LOG.info("Downloaded %s (%d/%d PDFs)", url, len(results), len(urls))
            except Exception as exc:
                results[url] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
                LOG.error("%s: %s", url, exc)
            atomic_json(root / "syllabus_progress.json", {"updated_at": now(), "requested_urls": len(urls), "results": results})
    collected = []
    for row in rows:
        record = {"manifest_record": row, "id": row["id"]}
        if row.get("syllabus_url"):
            record.update(results[row["syllabus_url"]])
        else:
            record.update(status="missing_url", error="No syllabus URL supplied; no absence-of-syllabus claim is inferred")
        collected.append(record)
    write_jsonl(root / "syllabi.jsonl", collected)
    report = {
        "collector_version": VERSION, "finished_at": now(),
        "input_manifest": str(args.manifest), "requested_manifest_records": len(rows),
        "unique_requested_urls": len(urls),
        "downloaded_unique_pdfs": sum(item["status"] == "downloaded" for item in results.values()),
        "failed_unique_urls": sum(item["status"] == "failed" for item in results.values()),
        "missing_url_records": sum(item["status"] == "missing_url" for item in collected),
        "output": "syllabi.jsonl", "network_requests": client.network_requests, "cache_hits": client.cache_hits,
        "coverage_note": "Coverage is limited to the explicitly supplied manifest, not all UTD courses or sections. Course/term labels come from the manifest; the collector verifies PDF bytes, not the academic metadata or teaching content.",
    }
    atomic_json(root / "syllabus_report.json", report)
    print(json.dumps(report, indent=2))
    return 0 if not report["failed_unique_urls"] and not report["missing_url_records"] else 2


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog", help="Collect official undergraduate/graduate catalog descriptions")
    catalog.add_argument("--year", type=int, default=datetime.now().year)
    catalog.add_argument("--levels", nargs="+", choices=["undergraduate", "graduate"], default=["undergraduate", "graduate"])
    catalog.add_argument("--prefixes", nargs="+", type=str.upper, help="Optional prefix subset, e.g. CS SE MATH")
    catalog.set_defaults(run=collect_catalog)
    syllabi = sub.add_parser("syllabi", help="Download public syllabus URLs supplied in a JSONL manifest")
    syllabi.add_argument("--manifest", type=Path, required=True)
    syllabi.set_defaults(run=collect_syllabi)
    for command in [catalog, syllabi]:
        command.add_argument("--output", type=Path, default=Path("data"))
        command.add_argument("--workers", type=int, choices=range(1, 5), default=3)
        command.add_argument("--delay", type=float, default=1.0, help="Minimum seconds between network requests")
        command.add_argument("--timeout", type=float, default=30)
        command.add_argument("--retries", type=int, default=2)
        command.add_argument("--refresh", action="store_true", help="Fetch fresh source pages rather than reuse validated checkpoints")
    return cli


def main():
    cli = parser()
    args = cli.parse_args()
    if args.delay < 0.5 or args.timeout <= 0 or args.retries < 0:
        cli.error("delay must be at least 0.5s, timeout positive, and retries nonnegative")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        return args.run(args)
    except (CollectionError, OSError, ValueError) as exc:
        LOG.error("%s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
