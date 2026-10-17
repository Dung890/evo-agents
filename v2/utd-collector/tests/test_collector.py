"""Offline regression checks for loss of source text and false-success downloads."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collector import CollectionError, HttpStore, check_url, load_manifest, parse_catalog, parse_prefixes


PREFIX = {
    "prefix": "CS", "prefix_name": "Computer Science", "school": "Engineering",
    "catalog_year": 2026, "level": "undergraduate",
    "url": "https://catalog.utdallas.edu/2026/undergraduate/courses/cs",
}
META = {"path": "raw/source.html", "sha256": "example-sha", "retrieved_at": "2026-10-17T00:00:00+00:00"}
COURSE = b'''<html><div id="bukku-page"><h1>Computer Science</h1>
<p id="cs2v95"><span class="course_address"><a href="/2026/undergraduate/courses/cs2v95">CS 2V95</a>
(<a href="/2026/undergraduate/courses/ce2v95">CE 2V95</a>)</span>
<span class="course_title">Topics &amp; Methods</span> <span class="course_hours">(1-6 semester credit hours)</span>
Methods in <em>graph</em> analysis. Prerequisite: <a href="/2026/undergraduate/courses/cs1337">CS 1337</a>.
May be repeated. (Same as CE 2V95) (1-6) R</p></div></html>'''


class CatalogTests(unittest.TestCase):
    def test_description_preserves_nested_links_and_end_notes(self):
        records = parse_catalog(COURSE, PREFIX, META)
        self.assertEqual(len(records), 1)
        row = records[0]
        self.assertEqual(row["course_id"], "CS2V95")
        self.assertEqual(row["course_number"], "2V95")
        self.assertEqual(row["title"], "Topics & Methods")
        self.assertEqual(row["description_text"], "Methods in graph analysis. Prerequisite: CS 1337. May be repeated. (Same as CE 2V95) (1-6) R")
        self.assertEqual(row["equivalent_course_references"], ["CE 2V95"])
        self.assertEqual(row["credit_hours_text"], "(1-6 semester credit hours)")
        self.assertEqual(row["raw_source_path"], "raw/source.html")

    def test_prefix_discovery_ignores_navigation_and_school_links(self):
        source = b'''<html><a href="/2026/undergraduate/courses/notaprefix">navigation</a>
<div id="bukku-page"><table><tr><td><a href="/2026/undergraduate/courses/cs">CS</a></td>
<td>Computer Science</td><td><a href="/2026/undergraduate/courses/school/ecs">Engineering</a></td></tr></table></div></html>'''
        self.assertEqual(parse_prefixes(source, 2026, "undergraduate"), [PREFIX])

    def test_genuine_empty_prefix_is_distinguished_from_changed_markup(self):
        self.assertEqual(parse_catalog(b'<html><div id="bukku-page"><h1>Computer Science</h1></div></html>', PREFIX, META), [])
        for body in [b'<html><div id="bukku-page"><h1>Unavailable</h1></div></html>', b'<html><div id="bukku-page"><h1>Computer Science</h1><p>New course markup</p></div></html>']:
            with self.assertRaises(CollectionError):
                parse_catalog(body, PREFIX, META)

    def test_wrong_primary_course_identifier_is_rejected(self):
        with self.assertRaises(CollectionError):
            parse_catalog(COURSE.replace(b'/courses/cs2v95', b'/courses/math2413'), PREFIX, META)

    def test_identical_duplicates_are_merged_with_source_occurrences_preserved(self):
        duplicated = COURSE.replace(b'</div>', COURSE[COURSE.index(b'<p '):COURSE.index(b'</p>') + 4] + b'</div>')
        records = parse_catalog(duplicated, PREFIX, META)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['source_occurrences'], 2)
        self.assertIn('identical_duplicate_in_source_page', records[0]['source_warnings'])

    def test_conflicting_duplicates_are_rejected(self):
        second = COURSE[COURSE.index(b'<p '):COURSE.index(b'</p>') + 4].replace(b'Topics &amp; Methods', b'Conflicting Title')
        duplicated = COURSE.replace(b'</div>', second + b'</div>')
        with self.assertRaises(CollectionError):
            parse_catalog(duplicated, PREFIX, META)

    def test_incorrect_html_anchor_does_not_override_the_primary_course_link(self):
        record = parse_catalog(COURSE.replace(b'id="cs2v95"', b'id="sysm6315"'), PREFIX, META)[0]
        self.assertEqual(record['course_id'], 'CS2V95')
        self.assertEqual(record['source_html_anchor'], 'sysm6315')
        self.assertIn('source_html_anchor_differs_from_course_code', record['source_warnings'])

    def test_unclosed_equivalence_span_preserves_description_and_equivalent_courses(self):
        source = b'''<html><div id="bukku-page"><p id="cs2v95">
<span class="course_address"><a href="/2026/undergraduate/courses/cs2v95">CS 2V95</a></span>
<span class="course_tccns">(<a href="/2026/undergraduate/courses/ce2v95">CE 2V95</a>
<span class="course_title">Topics</span><span class="course_hours">(1-6 semester credit hours)</span>
Description with <em>nested</em> text. Prerequisite: <a href="/2026/undergraduate/courses/cs1337">CS 1337</a>.
</p></div></html>'''
        record = parse_catalog(source, PREFIX, META)[0]
        self.assertEqual(record['description_text'], 'Description with nested text. Prerequisite: CS 1337.')
        self.assertEqual(record['equivalent_course_references'], ['CE 2V95'])
        self.assertIn('source_course_title_has_nested_markup', record['source_warnings'])


class DownloadTests(unittest.TestCase):
    def test_html_login_empty_and_truncated_pdf_cannot_be_successes(self):
        for data, kind in [(b"", "html"), (b'<html>You must be signed in to view this page</html>', "html"), (b'<html>Login</html>', "pdf"), (b'%PDF-1.7\npartial content', "pdf")]:
            with self.assertRaises(CollectionError):
                HttpStore.validate(data, kind)
        HttpStore.validate(b'%PDF-1.7\ncomplete mock bytes\n%%EOF', "pdf")

    def test_login_redirect_and_unexpected_hosts_are_rejected(self):
        for url in ['https://wat.utdallas.edu/login/catbook', 'https://other.example/file.pdf', 'http://catalog.utdallas.edu/2026', 'https://user:password@catalog.utdallas.edu/2026']:
            with self.assertRaises(CollectionError):
                check_url(url)

    def test_resume_reuses_original_provenance_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            client = HttpStore(directory)
            source = b'<html><p>Saved course description</p></html>'
            url = PREFIX['url']
            _, meta = client.save_response(url, source, retrieved_at="2026-10-17T00:00:00+00:00")
            with patch('urllib.request.build_opener', side_effect=AssertionError('network should not run')):
                data, resumed = client.fetch(url)
            self.assertEqual(data, source)
            self.assertEqual(resumed, meta)
            self.assertEqual(client.cache_hits, 1)

    def test_corrupt_checkpoint_is_refetched(self):
        with tempfile.TemporaryDirectory() as directory:
            client = HttpStore(directory, delay=0, retries=0)
            _, meta = client.save_response(PREFIX['url'], b'<html><p>Original</p></html>')
            (Path(directory) / meta['path']).write_bytes(b'<html><p>Corrupted</p></html>')
            with patch('urllib.request.build_opener', side_effect=CollectionError('network refetch attempted')):
                with self.assertRaisesRegex(CollectionError, 'network refetch attempted'):
                    client.fetch(PREFIX['url'])

    def test_missing_urls_remain_explicit_and_duplicate_manifest_ids_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.jsonl'
            path.write_text(json.dumps({'id': 'missing', 'syllabus_url': None}) + '\n')
            self.assertIsNone(load_manifest(path)[0]['syllabus_url'])
            path.write_text('{"id":"duplicate"}\n{"id":"duplicate"}\n')
            with self.assertRaises(CollectionError):
                load_manifest(path)


if __name__ == '__main__':
    unittest.main()
