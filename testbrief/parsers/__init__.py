"""Input parsers. Each one turns a report file into a `Report`."""

from testbrief.parsers.junit import parse_junit
from testbrief.parsers.newman import parse_newman

PARSERS = {
    "junit": parse_junit,
    "newman": parse_newman,
}

__all__ = ["PARSERS", "parse_junit", "parse_newman"]
