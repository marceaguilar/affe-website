#!/usr/bin/env python3
"""
Build the AFFE "New Research" feed.

Harvests recent field-experiment papers in economics, finance, accounting and
business from two bibliographic databases, cross-verifies every record against
both, and writes a static JSON file that the /new-research page reads.

    Sources
    -------
    Journals : OpenAlex, restricted to the ISSN allowlist in config.yml.
    SSRN     : Crossref, restricted to DOI prefix 10.2139 (SSRN's prefix).

    Verification
    ------------
    Nothing is published unless its DOI resolves in BOTH OpenAlex and Crossref
    and the two agree on the title. Records that resolve in only one database
    are dropped and counted in the run report. This is what the "verified"
    badge on the page means.

Usage
-----
    python3 tools/new-research/build.py                # normal run
    python3 tools/new-research/build.py --dry-run      # report only, no write
    python3 tools/new-research/build.py --summaries llm  # needs ANTHROPIC_API_KEY

Only dependency beyond the standard library is PyYAML.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "config.yml"
OUTPUT_PATH = ROOT / "assets" / "data" / "new-research.json"

OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"
SSRN_PREFIX = "10.2139"

USER_AGENT = "affe-website-new-research/1.0 (+https://accfinfe.com)"


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

class Http:
    """Tiny polite HTTP client with retries and a courtesy delay."""

    def __init__(self, email: str, delay: float = 0.12):
        self.email = email
        self.delay = delay
        self.calls = 0

    def get_json(self, url: str, retries: int = 4):
        last_error = None
        for attempt in range(retries):
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": f"{USER_AGENT} mailto:{self.email}",
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = json.load(response)
                self.calls += 1
                time.sleep(self.delay)
                return payload
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code in (429, 500, 502, 503, 504):
                    time.sleep(2 ** attempt)
                    continue
                if error.code == 404:
                    return None
                raise
            except Exception as error:  # network hiccups
                last_error = error
                time.sleep(2 ** attempt)
        print(f"  ! giving up on {url[:110]} ({last_error})", file=sys.stderr)
        return None


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

JATS_TAG = re.compile(r"<[^>]+>")
WHITESPACE = re.compile(r"\s+")
# Abstracts routinely arrive with the space after a full stop missing, which
# breaks sentence splitting ("...performance.We find that...").
GLUED_SENTENCE = re.compile(r"([a-z0-9\)\]])([.!?])([A-Z])")


def clean_text(raw: str | None) -> str:
    """Strip JATS/HTML markup and normalise whitespace."""
    if not raw:
        return ""
    text = JATS_TAG.sub(" ", raw)
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = GLUED_SENTENCE.sub(r"\1\2 \3", text)
    return WHITESPACE.sub(" ", text).strip()


def reconstruct_abstract(inverted_index: dict | None) -> str:
    """OpenAlex stores abstracts as an inverted index. Put it back together."""
    if not inverted_index:
        return ""
    positions: dict[int, str] = {}
    for word, spots in inverted_index.items():
        for spot in spots:
            positions[spot] = word
    if not positions:
        return ""
    return " ".join(positions[key] for key in sorted(positions))


TITLE_PREFIX = re.compile(
    r"^\s*(express|frontiers|editorial|invited paper|research note|abstract)\s*[:\-\u2013]\s*",
    re.I,
)
ABSTRACT_PREFIX = re.compile(r"^\s*(abstract|summary|purpose)\b[\s:.\-\u2013]*", re.I)


def tidy_title(raw: str | None) -> str:
    """Drop publisher prefixes such as 'EXPRESS:' that journals bolt onto titles."""
    text = clean_text(raw)
    for _ in range(2):
        text = TITLE_PREFIX.sub("", text)
    return text.strip()


def tidy_abstract(raw: str | None) -> str:
    """Drop the literal word 'Abstract' that some publishers embed in the text."""
    return ABSTRACT_PREFIX.sub("", clean_text(raw)).strip()


def normalise_title(title: str) -> str:
    """Aggressive normalisation used for cross-database title agreement."""
    text = unicodedata.normalize("NFKD", clean_text(title).lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", text)


def phrase_pattern(phrase: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(phrase).replace(r"\ ", r"[\s\-]+") + r"\b", re.I)


# --------------------------------------------------------------------------
# Screening
# --------------------------------------------------------------------------

class Screener:
    """Decides whether a harvested record is an in-scope field experiment."""

    def __init__(self, config: dict):
        self.strong = [
            phrase_pattern(p)
            for p in config["field_experiment_phrases"]
            if p not in set(config.get("weak_phrases", []))
        ]
        self.weak = [phrase_pattern(p) for p in config.get("weak_phrases", [])]
        self.exclusions = [phrase_pattern(p) for p in config.get("exclusion_keywords", [])]
        self.disciplines = {
            name: [phrase_pattern(k) for k in keywords]
            for name, keywords in config["discipline_keywords"].items()
        }

    def matched_method(self, text: str) -> tuple[bool, bool]:
        """Return (has_strong_match, has_weak_match)."""
        strong = any(p.search(text) for p in self.strong)
        weak = any(p.search(text) for p in self.weak)
        return strong, weak

    def excluded(self, text: str) -> str | None:
        for pattern in self.exclusions:
            found = pattern.search(text)
            if found:
                return found.group(0).lower()
        return None

    def disciplines_matched(self, text: str) -> list[str]:
        return [
            name
            for name, patterns in self.disciplines.items()
            if any(p.search(text) for p in patterns)
        ]


# --------------------------------------------------------------------------
# Harvest: journals via OpenAlex
# --------------------------------------------------------------------------

def harvest_journals(http: Http, config: dict, report: dict) -> list[dict]:
    journals = config["journals"]
    by_issn = {j["issn"].upper(): j for j in journals}
    since = (
        dt.date.today() - dt.timedelta(days=config["lookback_days"]["journals"])
    ).isoformat()

    records: list[dict] = []
    # OpenAlex caps OR-lists at 50 values per filter key.
    for batch_start in range(0, len(journals), 40):
        batch = journals[batch_start:batch_start + 40]
        issn_filter = "|".join(j["issn"] for j in batch)
        cursor = "*"
        while cursor:
            params = {
                "filter": (
                    f"primary_location.source.issn:{issn_filter},"
                    f"from_publication_date:{since},"
                    f"title_and_abstract.search:\"field experiment\"|"
                    f"\"randomized controlled trial\"|\"randomised controlled trial\"|"
                    f"\"randomized experiment\"|\"audit study\"|\"correspondence study\"|"
                    f"\"cluster randomized\"|\"randomized evaluation\""
                ),
                "per-page": "200",
                "cursor": cursor,
                "mailto": http.email,
            }
            url = f"{OPENALEX}/works?" + urllib.parse.urlencode(params, safe='|:"')
            payload = http.get_json(url)
            if not payload:
                break
            for work in payload.get("results", []):
                source = (work.get("primary_location") or {}).get("source") or {}
                issns = [str(i).upper() for i in (source.get("issn") or [])]
                issns.append(str(source.get("issn_l") or "").upper())
                journal = next((by_issn[i] for i in issns if i in by_issn), None)
                if journal is None:
                    continue
                records.append(_from_openalex(work, journal))
            cursor = (payload.get("meta") or {}).get("next_cursor")
            if not payload.get("results"):
                break

    report["harvested_journals"] = len(records)
    return records


def _from_openalex(work: dict, journal: dict) -> dict:
    doi = (work.get("doi") or "").replace("https://doi.org/", "").lower()
    authors = [
        clean_text((a.get("author") or {}).get("display_name"))
        for a in work.get("authorships", [])
    ]
    return {
        "doi": doi,
        "title": tidy_title(work.get("title") or work.get("display_name")),
        "abstract": tidy_abstract(reconstruct_abstract(work.get("abstract_inverted_index"))),
        "authors": [a for a in authors if a],
        "year": work.get("publication_year"),
        "date": work.get("publication_date") or "",
        "venue_kind": "journal",
        "venue": journal["name"],
        "venue_short": journal["short"],
        "discipline": journal["discipline"],
        "openalex_id": work.get("id"),
        "_seen_in": {"openalex"},
    }


# --------------------------------------------------------------------------
# Harvest: SSRN via Crossref
# --------------------------------------------------------------------------

SSRN_QUERIES = [
    "field experiment",
    "randomized controlled trial",
    "randomized field experiment",
    "audit study",
    "correspondence study",
]


def harvest_ssrn(http: Http, config: dict, report: dict) -> list[dict]:
    since = (
        dt.date.today() - dt.timedelta(days=config["lookback_days"]["ssrn"])
    ).isoformat()

    seen: dict[str, dict] = {}
    for query in SSRN_QUERIES:
        cursor = "*"
        pages = 0
        while cursor and pages < 5:
            params = {
                "query.bibliographic": query,
                "filter": f"prefix:{SSRN_PREFIX},from-created-date:{since}",
                "rows": "200",
                "cursor": cursor,
                "mailto": http.email,
            }
            url = f"{CROSSREF}/works?" + urllib.parse.urlencode(params)
            payload = http.get_json(url)
            if not payload:
                break
            message = payload.get("message", {})
            items = message.get("items", [])
            if not items:
                break
            for item in items:
                record = _from_crossref(item)
                if record and record["doi"] not in seen:
                    seen[record["doi"]] = record
            cursor = message.get("next-cursor")
            pages += 1

    report["harvested_ssrn"] = len(seen)
    return list(seen.values())


def _date_parts(node: dict | None) -> tuple[str, int]:
    """Return (ISO date, number of parts the source actually supplied).

    Crossref pads missing months and days, so a bare year and a real date look
    identical once formatted. The part count tells us which we got.
    """
    if not node:
        return "", 0
    parts = (node.get("date-parts") or [[]])[0]
    if not parts:
        return "", 0
    supplied = len([x for x in parts if x is not None])
    padded = list(parts) + [1, 1]
    try:
        return dt.date(int(padded[0]), int(padded[1]), int(padded[2])).isoformat(), supplied
    except (ValueError, TypeError):
        return "", 0


def _best_date(item: dict) -> str:
    """Pick the most precise date Crossref offers for an SSRN posting.

    SSRN usually reports `posted` as a bare year, which would collapse every
    working paper onto 1 January and make the date filter and the sort order
    meaningless. When `posted` is year-only we fall back to `created`, the day
    the record was deposited, which tracks the posting date closely.
    """
    posted, posted_parts = _date_parts(item.get("posted"))
    created, created_parts = _date_parts(item.get("created"))
    if posted_parts >= 3:
        return posted
    if created_parts >= 3:
        # Keep the posted year if the two disagree, since that is the year the
        # authors dated the paper.
        if posted and posted[:4] != created[:4]:
            return posted
        return created
    return posted or created


def _from_crossref(item: dict) -> dict | None:
    doi = (item.get("DOI") or "").lower()
    if not doi:
        return None
    titles = item.get("title") or []
    title = tidy_title(titles[0] if titles else "")
    if not title:
        return None
    authors = []
    for person in item.get("author", []) or []:
        name = clean_text(f"{person.get('given', '')} {person.get('family', '')}".strip())
        if not name:
            name = clean_text(person.get("name"))
        if name:
            authors.append(name)
    posted = _best_date(item)
    return {
        "doi": doi,
        "title": title,
        "abstract": tidy_abstract(item.get("abstract")),
        "authors": authors,
        "year": int(posted[:4]) if posted[:4].isdigit() else None,
        "date": posted,
        "venue_kind": "ssrn",
        "venue": "SSRN working paper",
        "venue_short": "SSRN",
        "discipline": None,
        "openalex_id": None,
        "_seen_in": {"crossref"},
    }


# --------------------------------------------------------------------------
# Cross-database verification
# --------------------------------------------------------------------------

def verify(http: Http, record: dict, report: dict) -> bool:
    """Confirm the DOI resolves in both databases and titles agree.

    Fills in `verified_in`, and for SSRN records also fills the discipline
    and abstract using whichever database has them.
    """
    doi = record["doi"]
    confirmed = set(record["_seen_in"])

    # --- Crossref side ----------------------------------------------------
    if "crossref" not in confirmed:
        payload = http.get_json(f"{CROSSREF}/works/{urllib.parse.quote(doi)}?mailto={http.email}")
        item = (payload or {}).get("message")
        if item:
            titles = item.get("title") or []
            other = normalise_title(titles[0] if titles else "")
            if other and _titles_agree(normalise_title(record["title"]), other):
                confirmed.add("crossref")
                if not record["abstract"]:
                    record["abstract"] = tidy_abstract(item.get("abstract"))

    # --- OpenAlex side ----------------------------------------------------
    if "openalex" not in confirmed:
        payload = http.get_json(f"{OPENALEX}/works/doi:{urllib.parse.quote(doi)}?mailto={http.email}")
        if payload and not payload.get("error"):
            other = normalise_title(payload.get("title") or payload.get("display_name") or "")
            if other and _titles_agree(normalise_title(record["title"]), other):
                confirmed.add("openalex")
                record["openalex_id"] = payload.get("id")
                record["cited_by_count"] = payload.get("cited_by_count", 0)
                if not record["abstract"]:
                    record["abstract"] = tidy_abstract(
                        reconstruct_abstract(payload.get("abstract_inverted_index"))
                    )
                topic = payload.get("primary_topic") or {}
                record["_openalex_field"] = ((topic.get("field") or {}).get("display_name") or "")
                record["_openalex_subfield"] = (
                    (topic.get("subfield") or {}).get("display_name") or ""
                )

    record["verified_in"] = sorted(confirmed)
    if len(confirmed) < 2:
        report["rejected_unverified"] += 1
        return False
    return True


def _titles_agree(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if left == right:
        return True
    # Publishers truncate and re-punctuate titles; accept a clean prefix match.
    shorter, longer = sorted((left, right), key=len)
    return len(shorter) >= 25 and longer.startswith(shorter)


# --------------------------------------------------------------------------
# Discipline assignment for SSRN records
# --------------------------------------------------------------------------

OPENALEX_FIELD_TO_DISCIPLINE = {
    "Economics, Econometrics and Finance": "economics",
    "Business, Management and Accounting": "management",
    "Decision Sciences": "management",
    "Social Sciences": None,  # too broad on its own; keyword gate decides
}


def assign_discipline(record: dict, screener: Screener, text: str) -> str | None:
    if record.get("discipline"):
        return record["discipline"]

    matched = screener.disciplines_matched(text)
    subfield = (record.get("_openalex_subfield") or "").lower()
    field = record.get("_openalex_field") or ""

    # Prefer the most specific signal available.
    if "accounting" in subfield and "accounting" in matched:
        return "accounting"
    if "finance" in subfield and "finance" in matched:
        return "finance"
    for candidate in ("accounting", "finance", "management", "economics"):
        if candidate in matched:
            return candidate
    return OPENALEX_FIELD_TO_DISCIPLINE.get(field)


IN_SCOPE_OPENALEX_FIELDS = {
    "Economics, Econometrics and Finance",
    "Business, Management and Accounting",
    "Decision Sciences",
    "Social Sciences",
    "Psychology",
}


# --------------------------------------------------------------------------
# Summaries
# --------------------------------------------------------------------------

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"\'])")

# Sentences that say what the researchers actually did.
DESIGN_CUES = (
    "field experiment", "randomized", "randomised", "rct", "audit study",
    "correspondence study", "we partner", "we conduct", "we run", "we ran",
    "we implement", "we test", "we examine", "we study", "we investigate",
    "we evaluate", "in collaboration with", "treatment arm", "control group",
    "we randomly", "at random", "experiment with", "we sent", "we mailed",
)
# Sentences that say what came out of it.
FINDING_CUES = (
    "we find", "we show", "we document", "we estimate", "results show",
    "results indicate", "results suggest", "findings show", "findings suggest",
    "we observe", "increases", "decreases", "reduces", "raises", "improves",
    "no effect", "null effect", "relative to the control", "treated",
    "percentage points", "effect size", "we detect",
)
MAX_SUMMARY_CHARS = 300
MIN_SENTENCE_CHARS = 35


def _split_sentences(abstract: str) -> list[str]:
    parts = [s.strip() for s in SENTENCE_SPLIT.split(abstract)]
    return [s for s in parts if len(s) >= MIN_SENTENCE_CHARS]


def _index_with(sentences, cues, start: int = 0):
    """Index of the first sentence at or after `start` that hits any cue."""
    for i in range(start, len(sentences)):
        lowered = sentences[i].lower()
        if any(cue in lowered for cue in cues):
            return i
    return -1


def _shorten(sentence: str, limit: int) -> str:
    if len(sentence) <= limit:
        return sentence
    return sentence[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "\u2026"


def extractive_summary(record: dict) -> str:
    """At most two sentences: what the study did, and what it found.

    Abstracts usually open with background prose that says nothing about the
    paper, so we look for a design sentence first and only fall back to the
    opening sentence when there is none.
    """
    abstract = record.get("abstract") or ""
    if not abstract:
        return ""

    sentences = _split_sentences(abstract)
    if not sentences:
        return _shorten(abstract.strip(), MAX_SUMMARY_CHARS)

    design_index = _index_with(sentences, DESIGN_CUES)
    if design_index < 0:
        design_index = 0
    design = sentences[design_index]

    # Only look for a result AFTER the design sentence. Searching the whole
    # abstract picks up background prose that happens to contain a verb like
    # "improves" and reads as if it were a finding of the paper.
    finding_index = _index_with(sentences, FINDING_CUES, start=design_index + 1)
    finding = sentences[finding_index] if finding_index >= 0 else None

    # Nothing cued as a result, but the summary would be very thin. Take the
    # next sentence so the reader gets more than a fragment.
    if finding is None and len(design) < 120 and design_index + 1 < len(sentences):
        finding = sentences[design_index + 1]

    summary = " ".join([design] + ([finding] if finding else []))
    if len(summary) <= MAX_SUMMARY_CHARS:
        return summary.strip()

    if finding and len(finding) <= MAX_SUMMARY_CHARS:
        budget = MAX_SUMMARY_CHARS - len(finding) - 1
        if budget >= 80:
            return f"{_shorten(design, budget)} {finding}".strip()
        return finding.strip()
    return _shorten(design, MAX_SUMMARY_CHARS)


DISCIPLINE_LABEL = {
    "accounting": "accounting",
    "finance": "finance",
    "economics": "economics",
    "management": "management and marketing",
}


def metadata_summary(record: dict) -> str:
    """Fallback for the handful of papers with no openly available abstract.

    Some publishers withhold abstracts from Crossref and OpenAlex alike, and
    they are not on Semantic Scholar either. Rather than drop a verified paper
    or invent a description, we state only what the metadata supports and mark
    it as such so the page can show it in a muted style.
    """
    field = DISCIPLINE_LABEL.get(record.get("discipline") or "", "business")
    if record["venue_kind"] == "journal":
        where = f"published in {record['venue']}"
    else:
        where = "posted as an SSRN working paper"
    return (
        f"Field experiment in {field}, {where}. "
        "No abstract is openly available, so no description could be extracted."
    )


def llm_summaries(records: list[dict]) -> None:
    """Optional: rewrite summaries with Claude. Requires ANTHROPIC_API_KEY.

    Falls back silently to the extractive summary for anything that fails, so
    a missing key or an API outage can never break the build.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ! ANTHROPIC_API_KEY not set; keeping extractive summaries", file=sys.stderr)
        return
    try:
        import anthropic  # type: ignore
    except ImportError:
        print("  ! anthropic package not installed; keeping extractive summaries", file=sys.stderr)
        return

    client = anthropic.Anthropic(api_key=api_key)
    todo = [r for r in records if r.get("abstract")]
    print(f"  summarising {len(todo)} abstracts with Claude")
    for record in todo:
        prompt = (
            "Summarise this research paper abstract in at most two short sentences "
            "(45 words total maximum) for a list of new field-experiment research. "
            "Say what was done and what was found. Use plain language. "
            "Do not add facts that are not in the abstract. "
            "Do not start with 'This paper' or 'The authors'. Return only the summary.\n\n"
            f"Title: {record['title']}\n\nAbstract: {record['abstract'][:6000]}"
        )
        try:
            message = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=180,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(
                block.text for block in message.content if getattr(block, "type", "") == "text"
            ).strip()
            if text:
                record["summary"] = text
                record["summary_source"] = "ai"
        except Exception as error:
            print(f"  ! summary failed for {record['doi']}: {error}", file=sys.stderr)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def build(args) -> int:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    if args.lookback_journals:
        config["lookback_days"]["journals"] = args.lookback_journals
    if args.lookback_ssrn:
        config["lookback_days"]["ssrn"] = args.lookback_ssrn
    if args.max_items:
        config["max_items"] = args.max_items
    http = Http(config["contact_email"])
    screener = Screener(config)
    report = {
        "harvested_journals": 0,
        "harvested_ssrn": 0,
        "rejected_not_field_experiment": 0,
        "rejected_out_of_scope": 0,
        "rejected_excluded_topic": 0,
        "rejected_unverified": 0,
        "rejected_too_old": 0,
    }

    print("Harvesting journals (OpenAlex)…")
    candidates = harvest_journals(http, config, report)
    print(f"  {report['harvested_journals']} journal records")

    print("Harvesting SSRN (Crossref)…")
    candidates += harvest_ssrn(http, config, report)
    print(f"  {report['harvested_ssrn']} SSRN records")

    # De-duplicate by DOI, preferring the journal version of a paper.
    by_doi: dict[str, dict] = {}
    for record in candidates:
        existing = by_doi.get(record["doi"])
        if existing is None or (
            existing["venue_kind"] == "ssrn" and record["venue_kind"] == "journal"
        ):
            by_doi[record["doi"]] = record
    candidates = list(by_doi.values())
    print(f"Screening {len(candidates)} unique DOIs…")

    # --- Stage 1: cheap text screening before any extra network calls -----
    stage_one: list[dict] = []
    for record in candidates:
        text = f"{record['title']} {record['abstract']}"
        strong, weak = screener.matched_method(text)
        if not (strong or weak):
            report["rejected_not_field_experiment"] += 1
            continue
        hit = screener.excluded(text)
        if hit:
            report["rejected_excluded_topic"] += 1
            continue
        if record["venue_kind"] == "ssrn":
            # SSRN is all-disciplines, so require a domain signal up front.
            if not screener.disciplines_matched(text):
                report["rejected_out_of_scope"] += 1
                continue
            if not strong:
                report["rejected_not_field_experiment"] += 1
                continue
        stage_one.append(record)

    print(f"  {len(stage_one)} passed text screening; verifying against both databases…")

    # --- Stage 2: cross-database verification ------------------------------
    min_year = config.get("min_year")
    verified: list[dict] = []
    for index, record in enumerate(stage_one, 1):
        if index % 25 == 0:
            print(f"    verified {index}/{len(stage_one)}")
        if not verify(http, record, report):
            continue

        text = f"{record['title']} {record['abstract']}"
        # Abstracts often arrive only at verification time; re-run exclusions.
        if screener.excluded(text):
            report["rejected_excluded_topic"] += 1
            continue
        if record["venue_kind"] == "ssrn":
            field = record.get("_openalex_field") or ""
            if field and field not in IN_SCOPE_OPENALEX_FIELDS:
                report["rejected_out_of_scope"] += 1
                continue

        discipline = assign_discipline(record, screener, text)
        if not discipline:
            report["rejected_out_of_scope"] += 1
            continue
        record["discipline"] = discipline

        if min_year and record.get("year") and record["year"] < min_year:
            report["rejected_too_old"] += 1
            continue

        verified.append(record)

    print(f"  {len(verified)} verified records")

    # --- Stage 3: summaries ------------------------------------------------
    for record in verified:
        summary = extractive_summary(record)
        if summary:
            record["summary"] = summary
            record["summary_source"] = "abstract"
        else:
            record["summary"] = metadata_summary(record)
            record["summary_source"] = "metadata"
    if args.summaries == "llm":
        llm_summaries(verified)

    # --- Stage 4: order and trim ------------------------------------------
    verified.sort(key=lambda r: (r.get("date") or "", r.get("year") or 0), reverse=True)
    verified = verified[: config["max_items"]]

    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "count": len(verified),
        "sources": {
            "journals": "OpenAlex",
            "working_papers": "Crossref (SSRN, DOI prefix 10.2139)",
            "verification": "Every entry resolves in both OpenAlex and Crossref with matching titles.",
        },
        "journals_tracked": [
            {"short": j["short"], "name": j["name"], "discipline": j["discipline"]}
            for j in config["journals"]
        ],
        "run_report": report,
        "papers": [_public_record(r) for r in verified],
    }

    from collections import Counter
    report["published"] = len(verified)
    report["published_by_source"] = dict(Counter(r["venue_kind"] for r in verified))
    report["published_by_discipline"] = dict(Counter(r["discipline"] for r in verified))
    report["published_without_summary"] = sum(1 for r in verified if not r.get("summary"))

    print("\nRun report")
    for key, value in report.items():
        print(f"  {key:34s} {value}")
    print(f"  {'api_calls':34s} {http.calls}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        _preview(verified)
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(f"\nWrote {OUTPUT_PATH.relative_to(ROOT)} ({len(verified)} papers)")
    return 0


def _public_record(record: dict) -> dict:
    return {
        "doi": record["doi"],
        "url": f"https://doi.org/{record['doi']}",
        "title": record["title"],
        "authors": record["authors"],
        "year": record.get("year"),
        "date": record.get("date") or "",
        "summary": record.get("summary") or "",
        "summary_source": record.get("summary_source", "abstract"),
        "venue": record["venue"],
        "venue_short": record["venue_short"],
        "venue_kind": record["venue_kind"],
        "discipline": record["discipline"],
        "verified_in": record.get("verified_in", []),
        "cited_by_count": record.get("cited_by_count", 0),
    }


def _preview(records: list[dict], limit: int = 12) -> None:
    print(f"\nFirst {min(limit, len(records))} entries:")
    for record in records[:limit]:
        authors = ", ".join(record["authors"][:3])
        if len(record["authors"]) > 3:
            authors += " et al."
        print(f"\n  [{record['discipline']}/{record['venue_short']}] {record.get('year')}")
        print(f"  {record['title']}")
        print(f"  {authors}")
        print(f"  {record.get('summary', '')[:220]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    parser.add_argument(
        "--summaries",
        choices=["abstract", "llm"],
        default="abstract",
        help="'abstract' extracts from the abstract (default); 'llm' rewrites with Claude",
    )
    parser.add_argument("--lookback-journals", type=int, help="override config lookback (days)")
    parser.add_argument("--lookback-ssrn", type=int, help="override config lookback (days)")
    parser.add_argument("--max-items", type=int, help="override config max_items")
    return build(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
