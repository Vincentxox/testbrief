import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from testbrief.models import Status
from testbrief.parsers import parse_junit, parse_newman

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
JUNIT = os.path.join(FIXTURES, "sample_junit.xml")
NEWMAN = os.path.join(FIXTURES, "sample_newman.json")


class JUnitParserTests(unittest.TestCase):
    def setUp(self):
        self.report = parse_junit(JUNIT)

    def test_counts_every_status(self):
        self.assertEqual(self.report.total, 5)
        self.assertEqual(self.report.passed, 2)
        self.assertEqual(self.report.failed, 1)
        self.assertEqual(self.report.errors, 1)
        self.assertEqual(self.report.skipped, 1)

    def test_pass_rate_ignores_skipped_tests(self):
        # 2 passed out of 4 executed tests
        self.assertAlmostEqual(self.report.pass_rate, 50.0)

    def test_keeps_messages_and_durations(self):
        failure = next(c for c in self.report.cases if c.status == Status.FAILED)
        self.assertEqual(failure.name, "rejects_expired_card")
        self.assertIn("402", failure.message)
        self.assertAlmostEqual(failure.duration, 2.10)

    def test_nested_suites_are_not_counted_twice(self):
        xml = (
            '<testsuite name="outer"><testsuite name="inner">'
            '<testcase name="a" classname="X"/></testsuite></testsuite>'
        )
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "nested.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(xml)
            self.assertEqual(parse_junit(path).total, 1)

    def test_rejects_other_xml(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "other.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("<html></html>")
            with self.assertRaises(ValueError):
                parse_junit(path)

    def test_malformed_xml_raises_parse_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "broken.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("<testsuite>")
            with self.assertRaises(ET.ParseError):
                parse_junit(path)


class NewmanParserTests(unittest.TestCase):
    def setUp(self):
        self.report = parse_newman(NEWMAN)

    def test_one_case_per_assertion_plus_request_errors(self):
        # 2 + 2 assertions, plus the request that never got a response
        self.assertEqual(self.report.total, 5)
        self.assertEqual(self.report.passed, 2)
        self.assertEqual(self.report.failed, 1)
        self.assertEqual(self.report.errors, 1)
        self.assertEqual(self.report.skipped, 1)

    def test_request_error_message_is_kept(self):
        error = next(c for c in self.report.cases if c.status == Status.ERROR)
        self.assertEqual(error.name, "GET /health")
        self.assertIn("ENOTFOUND", error.message)

    def test_assertions_are_grouped_by_request(self):
        failed = next(c for c in self.report.cases if c.status == Status.FAILED)
        self.assertEqual(failed.suite, "POST /items")

    def test_rejects_other_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "other.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"hello": "world"}, handle)
            with self.assertRaises(ValueError):
                parse_newman(path)


if __name__ == "__main__":
    unittest.main()
