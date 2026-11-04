import contextlib
import io
import os
import tempfile
import unittest

from testbrief.cli import EXIT_BAD_INPUT, EXIT_OK, EXIT_TEST_FAILURES, main
from testbrief.parsers import parse_junit
from testbrief.render import render_markdown

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
JUNIT = os.path.join(FIXTURES, "sample_junit.xml")
NEWMAN = os.path.join(FIXTURES, "sample_newman.json")


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class MarkdownRenderTests(unittest.TestCase):
    def test_summary_table_and_failures(self):
        text = render_markdown([parse_junit(JUNIT)])
        self.assertIn("# Test summary", text)
        self.assertIn("[FAIL]", text)
        self.assertIn("| 5 | 2 | 1 | 1 | 1 | 50.0% | 4.70s |", text)
        self.assertIn("rejects_expired_card", text)

    def test_pipes_in_messages_do_not_break_tables(self):
        text = render_markdown([parse_junit(JUNIT)])
        self.assertIn("ConnectionError \\| gateway unreachable", text)

    def test_slowest_section_can_be_disabled(self):
        text = render_markdown([parse_junit(JUNIT)], top_slowest=0)
        self.assertNotIn("Slowest", text)


class CliTests(unittest.TestCase):
    def test_prints_summary_for_both_formats(self):
        code, out, _ = run_cli(JUNIT, NEWMAN)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("2 report(s)", out)
        self.assertIn("JUnit XML", out)
        self.assertIn("Newman JSON", out)

    def test_fail_on_failures_sets_exit_code(self):
        code, _, _ = run_cli(JUNIT, "--fail-on-failures")
        self.assertEqual(code, EXIT_TEST_FAILURES)

    def test_writes_output_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "summary.md")
            code, out, _ = run_cli(JUNIT, "-o", target)
            self.assertEqual(code, EXIT_OK)
            self.assertEqual(out, "")
            with open(target, encoding="utf-8") as handle:
                self.assertIn("# Test summary", handle.read())

    def test_missing_file_is_a_clean_error(self):
        code, _, err = run_cli("does-not-exist.xml")
        self.assertEqual(code, EXIT_BAD_INPUT)
        self.assertIn("testbrief: error", err)

    def test_unknown_extension_asks_for_format(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "report.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("x")
            code, _, err = run_cli(path)
            self.assertEqual(code, EXIT_BAD_INPUT)
            self.assertIn("--format", err)


if __name__ == "__main__":
    unittest.main()
