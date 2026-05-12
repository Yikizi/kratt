#!/usr/bin/env python3
"""Check thesis terminology against Ekilex/Sonaveeb data."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_BASE = "https://ekilex.ee/api"
CACHE_DIR = Path(".cache/kratt/terms/ekilex")
DEFAULT_DATASETS = "esterm,eki,aso,TI,eõt,eiops,korpling,fon,kfs,rob,mat"


class TermCheckError(RuntimeError):
    pass


def cache_path(endpoint: str) -> Path:
    digest = hashlib.sha256(endpoint.encode("utf-8")).hexdigest()[:24]
    return CACHE_DIR / f"{digest}.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": data,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def request_json(endpoint: str, *, refresh: bool = False, timeout: float = 15.0) -> Any:
    cached = cache_path(endpoint)
    if cached.exists() and not refresh:
        return load_json(cached)["data"]

    api_key = os.environ.get("EKILEX_API_KEY", "").strip()
    if not api_key:
        raise TermCheckError(
            "EKILEX_API_KEY is not set. Export it before live Ekilex queries."
        )

    req = Request(
        f"{API_BASE}{endpoint}",
        headers={
            "Accept": "application/json",
            "ekilex-api-key": api_key,
            "User-Agent": "kratt-thesis-terms/1.0",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise TermCheckError(f"Ekilex HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise TermCheckError(f"Ekilex request failed: {exc.reason}") from exc

    write_json(cached, data)
    return data


def endpoint_for(mode: str, term: str, datasets: str | None) -> str:
    encoded_term = quote(term.strip(), safe="")
    if mode == "meaning":
        base = f"/meaning/search/{encoded_term}"
    elif mode == "word":
        base = f"/word/search/{encoded_term}"
    else:
        raise TermCheckError(f"Unsupported search mode: {mode}")

    if datasets:
        return f"{base}/{quote(datasets, safe=',')}"
    return base


def search_ekilex(
    term: str,
    *,
    mode: str = "meaning",
    datasets: str | None = DEFAULT_DATASETS,
    refresh: bool = False,
) -> dict[str, Any]:
    endpoint = endpoint_for(mode, term, datasets)
    return {
        "provider": "ekilex",
        "term": term,
        "mode": mode,
        "datasets": datasets,
        "endpoint": endpoint,
        "data": request_json(endpoint, refresh=refresh),
    }


def compact_values(data: Any, limit: int = 12) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def walk(node: Any, context: dict[str, Any] | None = None) -> None:
        context = context or {}
        if isinstance(node, dict):
            next_context = dict(context)
            for key in ("language", "languageCode", "lang", "datasetCode", "datasetCodes"):
                if key in node and node[key]:
                    next_context[key] = node[key]
            value = node.get("wordValue") or node.get("wordValuePrese")
            if value is None and (
                "wordId" in node or "lexemeId" in node or "homonymNumber" in node
            ):
                value = node.get("value")
            if isinstance(value, str) and value.strip():
                language = str(
                    node.get("language")
                    or node.get("languageCode")
                    or node.get("lang")
                    or context.get("language")
                    or context.get("lang")
                    or ""
                )
                datasets = node.get("datasetCodes") or node.get("datasetCode") or context.get(
                    "datasetCodes", ""
                )
                if isinstance(datasets, list):
                    dataset_text = ",".join(str(item) for item in datasets)
                else:
                    dataset_text = str(datasets or "")
                key = (value.strip(), language, dataset_text)
                if key not in seen:
                    seen.add(key)
                    values.append(
                        {
                            "value": value.strip(),
                            "language": language,
                            "datasets": dataset_text,
                        }
                    )
            for child in node.values():
                walk(child, next_context)
        elif isinstance(node, list):
            for child in node:
                walk(child, context)

    walk(data)
    return values[:limit]


def total_count(data: Any) -> int | None:
    if isinstance(data, dict) and isinstance(data.get("totalCount"), int):
        return data["totalCount"]
    if isinstance(data, dict) and isinstance(data.get("resultCount"), int):
        return data["resultCount"]
    if isinstance(data, dict) and isinstance(data.get("meaningCount"), int):
        return data["meaningCount"]
    for key in ("words", "meanings", "results"):
        if isinstance(data, dict) and isinstance(data.get(key), list):
            return len(data[key])
    return None


def print_search(result: dict[str, Any], *, raw: bool = False) -> None:
    if raw:
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
        return

    count = total_count(result["data"])
    count_text = "unknown" if count is None else str(count)
    print(f"{result['provider']} {result['mode']} search: {result['term']}")
    print(f"datasets: {result['datasets'] or 'all'}")
    print(f"matches: {count_text}")
    values = compact_values(result["data"])
    if values:
        print("values:")
        for item in values:
            suffix = []
            if item["language"]:
                suffix.append(item["language"])
            if item["datasets"]:
                suffix.append(item["datasets"])
            meta = f" ({'; '.join(suffix)})" if suffix else ""
            print(f"  - {item['value']}{meta}")


def strip_latex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\(?:cite|ref|label|url|href)(?:\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return text


def extract_terms_from_text(text: str) -> list[str]:
    terms: set[str] = set()

    for pattern in (
        r"\\(?:emph|textit|foreignlanguage\{english\})\{([^{}]{2,100})\}",
        r"\((?:inglise keeles|ingl\.?|inglise)\s+([^)]{2,100})\)",
    ):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            terms.add(clean_term(match.group(1)))

    stripped = strip_latex(text)
    for match in re.finditer(r"\(([A-Za-z][A-Za-z0-9 /-]{2,80})\)", stripped):
        candidate = clean_term(match.group(1))
        if looks_like_technical_term(candidate):
            terms.add(candidate)

    return sorted(term for term in terms if term)


def clean_term(term: str) -> str:
    term = re.sub(r"\s+", " ", term).strip(" .,;:()[]{}\"'")
    return term


def looks_like_technical_term(term: str) -> bool:
    if len(term) < 3 or len(term) > 80:
        return False
    lower = term.lower()
    markers = (
        "api",
        "model",
        "wake",
        "word",
        "false",
        "positive",
        "recall",
        "precision",
        "dataset",
        "training",
        "threshold",
        "voice",
        "assistant",
        "embedding",
        "neural",
        "network",
        "speech",
        "intent",
        "pipeline",
        "trigger",
    )
    return any(marker in lower for marker in markers) or bool(re.fullmatch(r"[A-Z0-9-]{2,}", term))


def read_terms(args: argparse.Namespace) -> list[str]:
    terms: list[str] = []
    for term in args.term or []:
        terms.append(clean_term(term))
    for terms_file in args.terms_file or []:
        for line in Path(terms_file).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                terms.append(clean_term(line))
    for input_file in args.files or []:
        text = Path(input_file).read_text(encoding="utf-8")
        terms.extend(extract_terms_from_text(text))

    unique: list[str] = []
    seen: set[str] = set()
    for term in terms:
        folded = term.casefold()
        if term and folded not in seen:
            seen.add(folded)
            unique.append(term)
    if args.limit:
        return unique[: args.limit]
    return unique


def run_check(args: argparse.Namespace) -> int:
    terms = read_terms(args)
    if not terms:
        raise TermCheckError("No terms found. Use --term, --terms-file, or input .tex files.")

    rows = []
    for term in terms:
        result = search_ekilex(
            term,
            mode=args.mode,
            datasets=args.datasets,
            refresh=args.refresh,
        )
        count = total_count(result["data"])
        values = compact_values(result["data"], limit=args.values)
        rows.append(
            {
                "term": term,
                "matches": count,
                "values": values,
                "endpoint": result["endpoint"],
            }
        )

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    for row in rows:
        count = row["matches"]
        status = "missing" if count == 0 else "found"
        count_text = "unknown" if count is None else str(count)
        print(f"{row['term']}\t{status}\t{count_text}")
        for item in row["values"]:
            suffix = []
            if item["language"]:
                suffix.append(item["language"])
            if item["datasets"]:
                suffix.append(item["datasets"])
            meta = f" ({'; '.join(suffix)})" if suffix else ""
            print(f"  - {item['value']}{meta}")
    return 0


def run_datasets(args: argparse.Namespace) -> int:
    data = request_json("/datasets", refresh=args.refresh)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                code = item.get("code") or item.get("datasetCode") or item.get("value") or "?"
                name = item.get("name") or item.get("description") or ""
                print(f"{code}\t{name}")
            else:
                print(item)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Estonian thesis terminology against Ekilex."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search one term in Ekilex")
    search.add_argument("term")
    search.add_argument("--mode", choices=("meaning", "word"), default="meaning")
    search.add_argument("--datasets", default=DEFAULT_DATASETS)
    search.add_argument("--all-datasets", action="store_true")
    search.add_argument("--refresh", action="store_true")
    search.add_argument("--raw", action="store_true")

    check = sub.add_parser("check", help="Check explicit terms or terms extracted from files")
    check.add_argument("files", nargs="*")
    check.add_argument("--term", action="append", help="Term to check; may be repeated")
    check.add_argument("--terms-file", action="append", help="One term per line")
    check.add_argument("--mode", choices=("meaning", "word"), default="meaning")
    check.add_argument("--datasets", default=DEFAULT_DATASETS)
    check.add_argument("--all-datasets", action="store_true")
    check.add_argument("--values", type=int, default=6)
    check.add_argument("--limit", type=int, default=50)
    check.add_argument("--refresh", action="store_true")
    check.add_argument("--json", action="store_true")

    datasets = sub.add_parser("datasets", help="List Ekilex datasets")
    datasets.add_argument("--refresh", action="store_true")
    datasets.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "all_datasets", False):
        args.datasets = None

    try:
        if args.command == "search":
            result = search_ekilex(
                args.term,
                mode=args.mode,
                datasets=args.datasets,
                refresh=args.refresh,
            )
            print_search(result, raw=args.raw)
            return 0
        if args.command == "check":
            return run_check(args)
        if args.command == "datasets":
            return run_datasets(args)
    except TermCheckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
