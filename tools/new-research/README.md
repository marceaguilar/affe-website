# New Research feed

Builds the data behind the **New Research** tab at
[accfinfe.com/new-research](https://accfinfe.com/new-research): recently posted
and recently published field experiments in accounting, finance, economics and
business.

```
tools/new-research/
  config.yml        <- the only file you normally need to edit
  build.py          <- the harvester
  requirements.txt
assets/data/new-research.json   <- generated output, committed to the repo
```

## How it works

The page is fully static. Nothing calls an external API at page load, so the
tab stays fast and cannot break when a third-party service goes down. All the
work happens ahead of time in `build.py`, which writes a single JSON file.

**Step 1 — Harvest.**

| Kind | Database | Restriction |
| --- | --- | --- |
| Journal articles | OpenAlex | the ISSN allowlist in `config.yml` |
| Working papers | Crossref | DOI prefix `10.2139`, which is SSRN's |

**Step 2 — Screen.** A record is kept only if its title or abstract contains an
explicit field-experiment term (`field experiment`, `randomized controlled
trial`, `audit study`, `correspondence study`, and the rest of the list in
`config.yml`). SSRN covers every discipline and agronomists run field
experiments too, so SSRN records must additionally match a discipline keyword
and must not match the exclusion vocabulary.

**Step 3 — Verify.** Every surviving DOI is looked up in *both* OpenAlex and
Crossref. A record is published only if it resolves in both and the two
databases report the same title. Anything that appears in only one database is
dropped and counted in the run report. This is what the green *Verified* badge
on the page means.

**Step 4 — Describe.** A one-or-two-sentence description is pulled from the
paper's own abstract: the sentence that says what the study did, plus the first
later sentence that says what it found.

**Step 5 — Write.** Results are sorted newest first, trimmed to `max_items`, and
written to `assets/data/new-research.json`.

## Running it

```bash
pip install -r tools/new-research/requirements.txt
python3 tools/new-research/build.py
```

Useful flags:

```bash
python3 tools/new-research/build.py --dry-run                 # report only, writes nothing
python3 tools/new-research/build.py --lookback-ssrn 30        # narrow the window while testing
python3 tools/new-research/build.py --max-items 20
python3 tools/new-research/build.py --summaries llm           # rewrite descriptions with Claude
```

A full run takes several minutes and makes a few hundred API calls. Both
databases are free and need no key; the script identifies itself with the
address in `config.yml` to stay in their polite pools.

## Automatic updates

`.github/workflows/new-research.yml` runs the build every Monday and Thursday
and commits the JSON if it changed. That commit triggers the normal Pages
deploy. You can also run it by hand from the repository's **Actions** tab.

## Changing what gets tracked

Everything tunable lives in `config.yml`.

- **Add a journal.** Append to `journals` with its ISSN-L. Confirm the ISSN
  first: `curl "https://api.openalex.org/sources/issn:0002-8282"` should return
  the journal you expect. The print or online ISSN will silently match nothing.
- **Broaden or tighten detection.** Edit `field_experiment_phrases`. Loosening
  these is the fastest way to fill the page with noise.
- **Kill a recurring false positive.** Add a word to `exclusion_keywords`.
- **Change the time window or list length.** `lookback_days` and `max_items`.

After any edit, run with `--dry-run` first and read the run report.

## Reading the run report

Every run prints counts for each rejection reason. `rejected_unverified` is the
one to watch: if it climbs sharply, one of the two databases is probably having
indexing trouble, not your config.

## Better descriptions, optionally

`--summaries llm` rewrites each description with Claude instead of extracting it
from the abstract. It needs `ANTHROPIC_API_KEY` in the environment and
`pip install anthropic`. If the key is missing or a call fails, the build keeps
the extracted description and carries on, so it can never break the site. Each
entry in the JSON records which path produced it in `summary_source`.
