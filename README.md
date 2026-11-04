# testbrief

A small command-line tool that turns test reports into a clean Markdown summary.
Point it at one or more report files and get totals, pass rate, a table of
failures and the slowest tests, ready to paste into a pull request, a ticket or
a CI job summary.

Zero runtime dependencies. Python 3.9+.

## Supported inputs

| Format | Produced by | Detected by |
|--------|-------------|-------------|
| JUnit XML | JUnit, TestNG, pytest (`--junitxml`), Jenkins, many others | `.xml` |
| Newman JSON | `newman run collection.json -r json --reporter-json-export out.json` | `.json` |

## Usage

```bash
python -m testbrief results.xml
python -m testbrief results.xml newman-out.json -o summary.md
python -m testbrief results.xml --fail-on-failures   # exit code 1 if anything failed
python -m testbrief report.dat --format junit         # force the format
```

Options:

| Option | Description |
|--------|-------------|
| `-f, --format {auto,junit,newman}` | Input format. Default: detect from the file extension. |
| `-o, --output FILE` | Write the summary to a file instead of stdout. |
| `--slowest N` | Show the N slowest tests when the report has timings (default 5, `0` hides it). |
| `--fail-on-failures` | Exit with code 1 when any test failed or errored. |

Exit codes: `0` ok, `1` failures found (with `--fail-on-failures`), `2` unreadable or unsupported input.

Try it with the sample reports:

```bash
python -m testbrief tests/fixtures/sample_junit.xml tests/fixtures/sample_newman.json
```

## Development

```bash
python -m unittest discover -s tests -t . -v
```

Layout:

```
testbrief/
  models.py          # Report and CaseResult
  parsers/           # one parser per input format
  render/            # one renderer per output format
  cli.py             # argument parsing and wiring
tests/               # unittest suite with small synthetic fixtures
```

All fixtures are synthetic. No real data is used anywhere in this repository.

## Roadmap

- [ ] HTML output (`--format html`) with collapsible failure details
- [ ] JMeter CSV/JTL input, with response-time percentiles
- [ ] Newman request timings in the slowest-tests table
- [ ] `--fail-under PERCENT` to gate on pass rate
- [ ] Compare two runs and report new failures, fixed tests and slowdowns
- [ ] Write a GitHub Actions job summary (`$GITHUB_STEP_SUMMARY`)
- [ ] JSON output for other tools
- [ ] Safer XML parsing for untrusted input

## License

MIT, see [LICENSE](LICENSE).
