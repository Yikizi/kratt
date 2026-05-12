#!/usr/bin/env python3
"""Summarize local coding-agent token usage for the Kratt thesis.

The script reads structured JSONL metadata from local Pi agent, Claude Code, and
Codex transcripts. It intentionally exports only usage counters and session
metadata, not prompts, assistant text, tool outputs, or file contents from the
conversations.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA_VERSION = 1
TOKEN_FIELDS = [
    "observed_context_tokens",
    "cache_excluded_tokens",
    "provider_input_tokens",
    "fresh_input_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "cache_write_5m_tokens",
    "cache_write_1h_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "cost_uncovered_observed_tokens",
]
COST_FIELDS = [
    "logged_cost_usd",
    "estimated_cost_usd",
]
TOTAL_FIELDS = TOKEN_FIELDS + COST_FIELDS
COUNTER_FIELDS = [
    "assistant_calls",
    "token_count_events",
    "files",
    "sessions",
    "files_without_usage",
    "parse_errors",
]


@dataclass
class TokenTotals:
    """Provider-normalized token counters.

    observed_context_tokens:
        Headline token traffic reported by the local tools. Includes cached input
        tokens when the provider/tool reports them as context usage.
    cache_excluded_tokens:
        observed_context_tokens minus cache-read tokens. This is closer to the
        amount of non-reused input/output work, while still counting cache
        creation/write tokens as fresh work.
    provider_input_tokens:
        Raw provider/tool input counter. Its exact cache semantics differ by
        tool, so prefer fresh_input_tokens/cache_read_tokens for cross-tool text.
    fresh_input_tokens:
        Input not served from cache, plus cache-write/cache-creation tokens.
    """

    observed_context_tokens: int = 0
    cache_excluded_tokens: int = 0
    provider_input_tokens: int = 0
    fresh_input_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    cache_write_5m_tokens: int = 0
    cache_write_1h_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    cost_uncovered_observed_tokens: int = 0
    logged_cost_usd: float = 0.0
    estimated_cost_usd: float = 0.0

    def add(self, other: "TokenTotals") -> None:
        for field_name in TOTAL_FIELDS:
            setattr(self, field_name, getattr(self, field_name) + getattr(other, field_name))

    def copy(self) -> "TokenTotals":
        copied = TokenTotals()
        copied.add(self)
        return copied

    def to_dict(self) -> Dict[str, int | float]:
        row: Dict[str, int | float] = {field_name: getattr(self, field_name) for field_name in TOKEN_FIELDS}
        row.update({field_name: round(getattr(self, field_name), 6) for field_name in COST_FIELDS})
        return row


@dataclass
class SessionRecord:
    tool: str
    session_file: str
    session_id: str = ""
    cwd: str = ""
    start_time: str = ""
    end_time: str = ""
    matched_reasons: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    providers: List[str] = field(default_factory=list)
    assistant_calls: int = 0
    token_count_events: int = 0
    parse_errors: int = 0
    file_size_bytes: int = 0
    totals: TokenTotals = field(default_factory=TokenTotals)

    def to_row(self) -> Dict[str, Any]:
        row: Dict[str, Any] = {
            "tool": self.tool,
            "session_file": self.session_file,
            "session_id": self.session_id,
            "cwd": self.cwd,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "matched_reasons": ";".join(sorted(set(self.matched_reasons))),
            "models": ";".join(sorted(set(self.models))),
            "providers": ";".join(sorted(set(self.providers))),
            "assistant_calls": self.assistant_calls,
            "token_count_events": self.token_count_events,
            "parse_errors": self.parse_errors,
            "file_size_bytes": self.file_size_bytes,
        }
        row.update(self.totals.to_dict())
        return row


@dataclass
class AggregateRow:
    key: Tuple[str, ...]
    totals: TokenTotals = field(default_factory=TokenTotals)
    assistant_calls: int = 0
    token_count_events: int = 0
    files: int = 0
    sessions: int = 0
    files_without_usage: int = 0
    parse_errors: int = 0

    def add_record(self, record: SessionRecord) -> None:
        self.totals.add(record.totals)
        self.assistant_calls += record.assistant_calls
        self.token_count_events += record.token_count_events
        self.files += 1
        self.sessions += 1
        if record.totals.observed_context_tokens == 0:
            self.files_without_usage += 1
        self.parse_errors += record.parse_errors

    def add_totals(self, totals: TokenTotals, *, assistant_calls: int = 0, token_count_events: int = 0) -> None:
        self.totals.add(totals)
        self.assistant_calls += assistant_calls
        self.token_count_events += token_count_events

    def to_dict(self, key_names: Sequence[str]) -> Dict[str, Any]:
        row: Dict[str, Any] = {name: value for name, value in zip(key_names, self.key)}
        row.update(self.totals.to_dict())
        row.update(
            {
                "assistant_calls": self.assistant_calls,
                "token_count_events": self.token_count_events,
                "files": self.files,
                "sessions": self.sessions,
                "files_without_usage": self.files_without_usage,
                "parse_errors": self.parse_errors,
            }
        )
        return row


@dataclass
class ScanResult:
    records: List[SessionRecord] = field(default_factory=list)
    by_tool: Dict[Tuple[str], AggregateRow] = field(default_factory=dict)
    by_model: Dict[Tuple[str, str, str], AggregateRow] = field(default_factory=dict)
    by_month: Dict[Tuple[str, str], AggregateRow] = field(default_factory=dict)

    def add_record(self, record: SessionRecord) -> None:
        self.records.append(record)
        tool_key = (record.tool,)
        self.by_tool.setdefault(tool_key, AggregateRow(tool_key)).add_record(record)
        month = month_from_record(record)
        month_key = (month, record.tool)
        self.by_month.setdefault(month_key, AggregateRow(month_key)).add_record(record)

    def add_model_totals(self, tool: str, provider: str, model: str, totals: TokenTotals, *, assistant_calls: int = 0, token_count_events: int = 0) -> None:
        key = (tool, provider or "unknown", model or "unknown")
        self.by_model.setdefault(key, AggregateRow(key)).add_totals(
            totals,
            assistant_calls=assistant_calls,
            token_count_events=token_count_events,
        )

    def grand_totals(self) -> TokenTotals:
        totals = TokenTotals()
        for record in self.records:
            totals.add(record.totals)
        return totals


@dataclass
class PriceEntry:
    provider_pattern: str
    model_pattern: str
    input_per_million: float
    output_per_million: float
    cache_read_per_million: float = 0.0
    cache_write_5m_per_million: float = 0.0
    cache_write_1h_per_million: float = 0.0
    source: str = ""


@dataclass
class MatchContext:
    project_root: Path
    project_name: str
    repo_owner: str = "Yikizi"
    price_entries: List[PriceEntry] = field(default_factory=list)
    since: Optional[datetime] = None
    until: Optional[datetime] = None

    @property
    def project_root_norm(self) -> str:
        return normalize_pathish(str(self.project_root))

    @property
    def project_name_lower(self) -> str:
        return self.project_name.lower()


@dataclass
class ParsedJsonLine:
    line_no: int
    obj: Optional[Dict[str, Any]]
    error: Optional[str] = None


def normalize_pathish(value: str) -> str:
    return value.replace("\\", "/").lower().rstrip("/")


def parse_time(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    text = value
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def iso_or_empty(value: Optional[datetime]) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_filter_time(value: Optional[str]) -> Optional[datetime]:
    if value is None or value == "":
        return None
    parsed = parse_time(value)
    if parsed is None:
        raise SystemExit(f"invalid ISO timestamp/date for time filter: {value}")
    return parsed


def time_in_scope(value: Optional[datetime], ctx: MatchContext) -> bool:
    if ctx.since is None and ctx.until is None:
        return True
    if value is None:
        return False
    if ctx.since is not None and value < ctx.since:
        return False
    if ctx.until is not None and value > ctx.until:
        return False
    return True


def update_time_range(current: Tuple[Optional[datetime], Optional[datetime]], candidate: Optional[datetime]) -> Tuple[Optional[datetime], Optional[datetime]]:
    if candidate is None:
        return current
    start, end = current
    if start is None or candidate < start:
        start = candidate
    if end is None or candidate > end:
        end = candidate
    return start, end


def int_value(mapping: Dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def float_value(mapping: Dict[str, Any], key: str) -> float:
    value = mapping.get(key)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def project_match_reasons(value: Any, ctx: MatchContext, label: str) -> List[str]:
    if not isinstance(value, str) or not value:
        return []
    text = normalize_pathish(value)
    reasons: List[str] = []
    project_root = ctx.project_root_norm
    name = re.escape(ctx.project_name_lower)

    if text == project_root or text.startswith(project_root + "/"):
        reasons.append(f"{label}:project-root")
    if re.search(rf"(^|[/_.-]){name}($|[/_.-])", text):
        reasons.append(f"{label}:project-name")
    # Claude Code stores project directories as -Users-name-kratt-...
    if f"-{ctx.project_name_lower}" in text or f"{ctx.project_name_lower}--" in text:
        reasons.append(f"{label}:encoded-project-name")
    owner_repo = f"{ctx.repo_owner.lower()}/{ctx.project_name_lower}"
    if owner_repo in text or f"{ctx.project_name_lower}.git" in text:
        reasons.append(f"{label}:repo-url")
    return reasons


def read_jsonl(path: Path) -> Iterable[ParsedJsonLine]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    yield ParsedJsonLine(line_no=line_no, obj=None, error=str(exc))
                    continue
                if isinstance(obj, dict):
                    yield ParsedJsonLine(line_no=line_no, obj=obj)
    except OSError as exc:
        yield ParsedJsonLine(line_no=0, obj=None, error=str(exc))


def infer_provider(model: str, fallback: str = "") -> str:
    model_lower = (model or "").lower()
    if model_lower.startswith("claude"):
        return "anthropic"
    if model_lower.startswith("gpt") or "codex" in model_lower:
        return "openai"
    return fallback or "unknown"


def load_price_entries(path: Path) -> Tuple[List[PriceEntry], Dict[str, Any]]:
    if not path.exists():
        return [], {"warning": f"price table not found: {path}"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries: List[PriceEntry] = []
    for item in payload.get("entries", []):
        if not isinstance(item, dict):
            continue
        entries.append(
            PriceEntry(
                provider_pattern=str(item.get("provider") or "*"),
                model_pattern=str(item.get("model_pattern") or "*"),
                input_per_million=float_value(item, "input_per_million"),
                output_per_million=float_value(item, "output_per_million"),
                cache_read_per_million=float_value(item, "cache_read_per_million"),
                cache_write_5m_per_million=float_value(item, "cache_write_5m_per_million"),
                cache_write_1h_per_million=float_value(item, "cache_write_1h_per_million"),
                source=str(item.get("source") or ""),
            )
        )
    return entries, {"path": str(path), "currency": payload.get("currency", "USD"), "notes": payload.get("notes", [])}


def find_price_entry(provider: str, model: str, entries: Sequence[PriceEntry]) -> Optional[PriceEntry]:
    provider_norm = provider or "unknown"
    model_norm = model or "unknown"
    for entry in entries:
        if fnmatch.fnmatchcase(provider_norm, entry.provider_pattern) and fnmatch.fnmatchcase(model_norm, entry.model_pattern):
            return entry
    return None


def apply_cost_estimate(totals: TokenTotals, provider: str, model: str, ctx: MatchContext) -> None:
    entry = find_price_entry(provider, model, ctx.price_entries)
    if entry is None:
        if totals.logged_cost_usd > 0:
            totals.estimated_cost_usd = totals.logged_cost_usd
        elif totals.observed_context_tokens > 0:
            totals.cost_uncovered_observed_tokens = totals.observed_context_tokens
        return

    # OpenAI/Codex token_count logs report input_tokens including cached input,
    # while Pi usage input excludes cacheRead. `fresh_input_tokens` normalizes both.
    input_tokens = totals.fresh_input_tokens if provider.startswith("openai") else totals.provider_input_tokens
    cache_write_5m = totals.cache_write_5m_tokens
    cache_write_1h = totals.cache_write_1h_tokens
    unsplit_cache_write = max(totals.cache_write_tokens - cache_write_5m - cache_write_1h, 0)
    cache_write_5m += unsplit_cache_write

    totals.estimated_cost_usd = (
        input_tokens * entry.input_per_million
        + totals.cache_read_tokens * entry.cache_read_per_million
        + cache_write_5m * entry.cache_write_5m_per_million
        + cache_write_1h * entry.cache_write_1h_per_million
        + totals.output_tokens * entry.output_per_million
    ) / 1_000_000


def pi_usage_to_totals(usage: Dict[str, Any]) -> TokenTotals:
    provider_input = int_value(usage, "input")
    output = int_value(usage, "output")
    cache_read = int_value(usage, "cacheRead")
    cache_write = int_value(usage, "cacheWrite")
    observed = int_value(usage, "totalTokens") or provider_input + output + cache_read + cache_write
    cost = usage.get("cost")
    logged_cost = float_value(cost, "total") if isinstance(cost, dict) else 0.0
    return TokenTotals(
        observed_context_tokens=observed,
        cache_excluded_tokens=max(observed - cache_read, 0),
        provider_input_tokens=provider_input,
        fresh_input_tokens=provider_input + cache_write,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
        output_tokens=output,
        logged_cost_usd=logged_cost,
    )


def claude_usage_to_totals(usage: Dict[str, Any]) -> TokenTotals:
    provider_input = int_value(usage, "input_tokens")
    cache_write = int_value(usage, "cache_creation_input_tokens")
    cache_read = int_value(usage, "cache_read_input_tokens")
    output = int_value(usage, "output_tokens")
    observed = provider_input + cache_write + cache_read + output
    cache_creation = usage.get("cache_creation")
    cache_write_5m = 0
    cache_write_1h = 0
    if isinstance(cache_creation, dict):
        cache_write_5m = int_value(cache_creation, "ephemeral_5m_input_tokens")
        cache_write_1h = int_value(cache_creation, "ephemeral_1h_input_tokens")
    if cache_write_5m + cache_write_1h > cache_write:
        cache_write_5m = min(cache_write_5m, cache_write)
        cache_write_1h = max(cache_write - cache_write_5m, 0)
    return TokenTotals(
        observed_context_tokens=observed,
        cache_excluded_tokens=max(observed - cache_read, 0),
        provider_input_tokens=provider_input,
        fresh_input_tokens=provider_input + cache_write,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
        cache_write_5m_tokens=cache_write_5m,
        cache_write_1h_tokens=cache_write_1h,
        output_tokens=output,
    )


def codex_usage_to_totals(usage: Dict[str, Any]) -> TokenTotals:
    provider_input = int_value(usage, "input_tokens")
    cache_read = int_value(usage, "cached_input_tokens")
    output = int_value(usage, "output_tokens")
    reasoning_output = int_value(usage, "reasoning_output_tokens")
    observed = int_value(usage, "total_tokens") or provider_input + output
    fresh_input = max(provider_input - cache_read, 0)
    return TokenTotals(
        observed_context_tokens=observed,
        cache_excluded_tokens=max(observed - cache_read, 0),
        provider_input_tokens=provider_input,
        fresh_input_tokens=fresh_input,
        cache_read_tokens=cache_read,
        cache_write_tokens=0,
        output_tokens=output,
        reasoning_output_tokens=reasoning_output,
    )


def totals_delta(current: TokenTotals, previous: TokenTotals) -> TokenTotals:
    delta = TokenTotals()
    for field_name in TOKEN_FIELDS:
        value = getattr(current, field_name) - getattr(previous, field_name)
        if value < 0:
            # Defensive fallback for a possible counter reset after compaction or
            # transcript splice: count the current cumulative value as a new run.
            value = getattr(current, field_name)
        setattr(delta, field_name, value)
    return delta


def month_from_record(record: SessionRecord) -> str:
    parsed = parse_time(record.start_time) or parse_time(record.end_time)
    if parsed is None:
        return "unknown"
    return parsed.strftime("%Y-%m")


def discover_jsonl_files(root: Path) -> List[Path]:
    if not root.exists():
        return []
    if root.is_file() and root.suffix == ".jsonl":
        return [root]
    return sorted(path for path in root.rglob("*.jsonl") if path.is_file())


def finalize_record_time(record: SessionRecord, time_range: Tuple[Optional[datetime], Optional[datetime]]) -> None:
    start, end = time_range
    record.start_time = iso_or_empty(start)
    record.end_time = iso_or_empty(end)


def scan_pi_sessions(root: Path, ctx: MatchContext, result: ScanResult) -> None:
    for path in discover_jsonl_files(root):
        record = SessionRecord(tool="pi", session_file=str(path), file_size_bytes=path.stat().st_size)
        record.matched_reasons.extend(project_match_reasons(str(path), ctx, "path"))
        time_range: Tuple[Optional[datetime], Optional[datetime]] = (None, None)
        model_totals: DefaultDict[Tuple[str, str], TokenTotals] = defaultdict(TokenTotals)
        model_calls: DefaultDict[Tuple[str, str], int] = defaultdict(int)

        for parsed in read_jsonl(path):
            if parsed.error:
                record.parse_errors += 1
                continue
            obj = parsed.obj or {}
            time_range = update_time_range(time_range, parse_time(obj.get("timestamp")))

            if obj.get("type") == "session":
                record.session_id = str(obj.get("id") or record.session_id)
                if isinstance(obj.get("cwd"), str):
                    record.cwd = str(obj.get("cwd"))
                    record.matched_reasons.extend(project_match_reasons(obj.get("cwd"), ctx, "cwd"))
                record.matched_reasons.extend(project_match_reasons(obj.get("parentSession"), ctx, "parent-session"))
                continue

            if obj.get("type") != "message" or not isinstance(obj.get("message"), dict):
                continue
            message = obj["message"]
            message_time = parse_time(message.get("timestamp")) or parse_time(obj.get("timestamp"))
            time_range = update_time_range(time_range, message_time)
            if message.get("role") != "assistant" or not isinstance(message.get("usage"), dict):
                continue
            if not time_in_scope(message_time, ctx):
                continue
            usage_totals = pi_usage_to_totals(message["usage"])
            record.assistant_calls += 1
            provider = str(message.get("provider") or "unknown")
            model = str(message.get("model") or "unknown")
            apply_cost_estimate(usage_totals, provider, model, ctx)
            record.totals.add(usage_totals)
            record.providers.append(provider)
            record.models.append(model)
            key = (provider, model)
            model_totals[key].add(usage_totals)
            model_calls[key] += 1

        finalize_record_time(record, time_range)
        if not record.matched_reasons:
            continue
        result.add_record(record)
        for (provider, model), totals in model_totals.items():
            result.add_model_totals("pi", provider, model, totals, assistant_calls=model_calls[(provider, model)])


def scan_claude_projects(root: Path, ctx: MatchContext, result: ScanResult) -> None:
    for path in discover_jsonl_files(root):
        record = SessionRecord(tool="claude_code", session_file=str(path), file_size_bytes=path.stat().st_size)
        record.matched_reasons.extend(project_match_reasons(str(path), ctx, "path"))
        time_range: Tuple[Optional[datetime], Optional[datetime]] = (None, None)
        model_totals: DefaultDict[Tuple[str, str], TokenTotals] = defaultdict(TokenTotals)
        model_calls: DefaultDict[Tuple[str, str], int] = defaultdict(int)

        for parsed in read_jsonl(path):
            if parsed.error:
                record.parse_errors += 1
                continue
            obj = parsed.obj or {}
            time_range = update_time_range(time_range, parse_time(obj.get("timestamp")))
            record.session_id = str(obj.get("sessionId") or record.session_id)
            if isinstance(obj.get("cwd"), str):
                if not record.cwd:
                    record.cwd = str(obj.get("cwd"))
                record.matched_reasons.extend(project_match_reasons(obj.get("cwd"), ctx, "cwd"))

            if obj.get("type") != "assistant" or not isinstance(obj.get("message"), dict):
                continue
            message = obj["message"]
            usage = message.get("usage")
            if not isinstance(usage, dict):
                continue
            event_time = parse_time(obj.get("timestamp"))
            if not time_in_scope(event_time, ctx):
                continue
            usage_totals = claude_usage_to_totals(usage)
            record.assistant_calls += 1
            model = str(message.get("model") or "unknown")
            provider = infer_provider(model)
            apply_cost_estimate(usage_totals, provider, model, ctx)
            record.totals.add(usage_totals)
            record.providers.append(provider)
            record.models.append(model)
            key = (provider, model)
            model_totals[key].add(usage_totals)
            model_calls[key] += 1

        finalize_record_time(record, time_range)
        if not record.matched_reasons:
            continue
        result.add_record(record)
        for (provider, model), totals in model_totals.items():
            result.add_model_totals("claude_code", provider, model, totals, assistant_calls=model_calls[(provider, model)])


def extract_codex_git_text(payload: Dict[str, Any]) -> str:
    git_value = payload.get("git")
    if isinstance(git_value, dict):
        selected = {
            key: git_value.get(key)
            for key in ("repository_url", "branch", "commit_hash")
            if key in git_value
        }
        return safe_json_dumps(selected)
    return ""


def scan_codex_sessions(roots: Sequence[Path], ctx: MatchContext, result: ScanResult) -> None:
    for root in roots:
        for path in discover_jsonl_files(root):
            record = SessionRecord(tool="codex", session_file=str(path), file_size_bytes=path.stat().st_size)
            record.matched_reasons.extend(project_match_reasons(str(path), ctx, "path"))
            time_range: Tuple[Optional[datetime], Optional[datetime]] = (None, None)
            current_model = "unknown"
            current_provider = "unknown"
            last_unique_totals = TokenTotals()
            seen_cumulative_keys = set()
            model_totals: DefaultDict[Tuple[str, str], TokenTotals] = defaultdict(TokenTotals)
            model_events: DefaultDict[Tuple[str, str], int] = defaultdict(int)

            for parsed in read_jsonl(path):
                if parsed.error:
                    record.parse_errors += 1
                    continue
                obj = parsed.obj or {}
                time_range = update_time_range(time_range, parse_time(obj.get("timestamp")))
                payload = obj.get("payload")
                if not isinstance(payload, dict):
                    continue

                if obj.get("type") == "session_meta":
                    record.session_id = str(payload.get("id") or record.session_id)
                    time_range = update_time_range(time_range, parse_time(payload.get("timestamp")))
                    if isinstance(payload.get("cwd"), str):
                        record.cwd = str(payload.get("cwd"))
                        record.matched_reasons.extend(project_match_reasons(payload.get("cwd"), ctx, "cwd"))
                    current_provider = str(payload.get("model_provider") or current_provider or "unknown")
                    git_text = extract_codex_git_text(payload)
                    record.matched_reasons.extend(project_match_reasons(git_text, ctx, "git"))
                    continue

                if obj.get("type") == "turn_context":
                    if isinstance(payload.get("cwd"), str):
                        if not record.cwd:
                            record.cwd = str(payload.get("cwd"))
                        record.matched_reasons.extend(project_match_reasons(payload.get("cwd"), ctx, "cwd"))
                    if isinstance(payload.get("model"), str):
                        current_model = str(payload.get("model"))
                        record.models.append(current_model)
                    current_provider = infer_provider(current_model, current_provider)
                    record.providers.append(current_provider)
                    continue

                if obj.get("type") != "event_msg" or payload.get("type") != "token_count":
                    continue
                info = payload.get("info")
                if not isinstance(info, dict):
                    continue
                cumulative = info.get("total_token_usage")
                if not isinstance(cumulative, dict):
                    continue

                event_time = parse_time(obj.get("timestamp"))
                current_totals = codex_usage_to_totals(cumulative)
                cumulative_key = tuple(getattr(current_totals, field_name) for field_name in TOKEN_FIELDS)
                if cumulative_key in seen_cumulative_keys:
                    continue
                seen_cumulative_keys.add(cumulative_key)
                delta = totals_delta(current_totals, last_unique_totals)
                last_unique_totals = current_totals.copy()
                if not time_in_scope(event_time, ctx):
                    continue
                record.token_count_events += 1
                provider = infer_provider(current_model, current_provider)
                model = current_model or "unknown"
                apply_cost_estimate(delta, provider, model, ctx)
                record.totals.add(delta)
                record.models.append(model)
                record.providers.append(provider)
                key = (provider, model)
                model_totals[key].add(delta)
                model_events[key] += 1

            finalize_record_time(record, time_range)
            if not record.matched_reasons:
                continue
            result.add_record(record)
            for (provider, model), totals in model_totals.items():
                result.add_model_totals("codex", provider, model, totals, token_count_events=model_events[(provider, model)])


def aggregate_rows_to_dicts(rows: Dict[Tuple[str, ...], AggregateRow], key_names: Sequence[str]) -> List[Dict[str, Any]]:
    return [rows[key].to_dict(key_names) for key in sorted(rows.keys())]


def totals_with_counters(records: Sequence[SessionRecord]) -> Dict[str, Any]:
    totals = TokenTotals()
    counters = {name: 0 for name in COUNTER_FIELDS}
    for record in records:
        totals.add(record.totals)
        counters["assistant_calls"] += record.assistant_calls
        counters["token_count_events"] += record.token_count_events
        counters["files"] += 1
        counters["sessions"] += 1
        counters["parse_errors"] += record.parse_errors
        if record.totals.observed_context_tokens == 0:
            counters["files_without_usage"] += 1
    output: Dict[str, Any] = totals.to_dict()
    output.update(counters)
    return output


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{100 * numerator / denominator:.1f}%"


def compact_tokens(value: int) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


def fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def write_markdown(path: Path, *, summary: Dict[str, Any], by_tool: Sequence[Dict[str, Any]], by_model: Sequence[Dict[str, Any]], by_month: Sequence[Dict[str, Any]], args: argparse.Namespace) -> None:
    totals = summary["totals"]
    lines: List[str] = []
    lines.append("# Kratt agent token usage summary")
    lines.append("")
    lines.append("This report is generated from local JSONL session metadata only. It does not export prompts, assistant responses, tool outputs, or conversation text.")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Metric", "Tokens", "Interpretation"],
            [
                ["Observed context tokens", fmt_int(totals["observed_context_tokens"]), "Provider/tool-reported context traffic, including cache-read tokens."],
                ["Cache-read tokens", fmt_int(totals["cache_read_tokens"]), "Repeated context served from provider/tool cache."],
                ["Cache-excluded tokens", fmt_int(totals["cache_excluded_tokens"]), "Observed context minus cache-read tokens."],
                ["Fresh input tokens", fmt_int(totals["fresh_input_tokens"]), "Input not served from cache, plus cache creation/write tokens."],
                ["Output tokens", fmt_int(totals["output_tokens"]), "Assistant output tokens reported by the tools."],
                ["Estimated token cost", fmt_usd(float(totals["estimated_cost_usd"])), "Token-equivalent USD estimate from the configured price table."],
                ["Logged token cost", fmt_usd(float(totals["logged_cost_usd"])), "Cost directly present in local logs, currently mostly Pi agent calls."],
            ],
        )
    )
    lines.append("")
    lines.append(
        f"Matched {totals['sessions']} Kratt-related session files. The cache-read share of observed context traffic is {pct(totals['cache_read_tokens'], totals['observed_context_tokens'])}."
    )
    lines.append("")
    lines.append("## By tool")
    lines.append("")
    tool_rows: List[List[str]] = []
    for row in sorted(by_tool, key=lambda item: item["observed_context_tokens"], reverse=True):
        tool_rows.append(
            [
                f"`{row['tool']}`",
                str(row["sessions"]),
                compact_tokens(row["observed_context_tokens"]),
                compact_tokens(row["cache_read_tokens"]),
                compact_tokens(row["cache_excluded_tokens"]),
                compact_tokens(row["output_tokens"]),
                fmt_usd(float(row["estimated_cost_usd"])),
            ]
        )
    lines.extend(markdown_table(["Tool", "Sessions", "Observed", "Cache read", "Cache-excluded", "Output", "Est. cost"], tool_rows))
    lines.append("")
    lines.append("## Top models")
    lines.append("")
    top_model_rows: List[List[str]] = []
    for row in sorted(by_model, key=lambda item: item["observed_context_tokens"], reverse=True)[:12]:
        top_model_rows.append(
            [
                f"`{row['tool']}`",
                f"`{row['model']}`",
                compact_tokens(row["observed_context_tokens"]),
                compact_tokens(row["cache_read_tokens"]),
                compact_tokens(row["cache_excluded_tokens"]),
                fmt_usd(float(row["estimated_cost_usd"])),
                str(row["assistant_calls"] or row["token_count_events"]),
            ]
        )
    lines.extend(markdown_table(["Tool", "Model", "Observed", "Cache read", "Cache-excluded", "Est. cost", "Calls/events"], top_model_rows))
    lines.append("")
    lines.append("## By month")
    lines.append("")
    month_rows: List[List[str]] = []
    for row in sorted(by_month, key=lambda item: (item["month"], item["tool"])):
        month_rows.append(
            [
                row["month"],
                f"`{row['tool']}`",
                str(row["sessions"]),
                compact_tokens(row["observed_context_tokens"]),
                compact_tokens(row["cache_read_tokens"]),
                compact_tokens(row["cache_excluded_tokens"]),
            ]
        )
    lines.extend(markdown_table(["Month", "Tool", "Sessions", "Observed", "Cache read", "Cache-excluded"], month_rows))
    lines.append("")
    lines.append("## Parser rules")
    lines.append("")
    lines.append("- Pi agent: sums `message.usage` on assistant messages in `~/.pi/agent/sessions/**/*.jsonl`, inside the optional time filter.")
    lines.append("- Claude Code: sums top-level `message.usage` on assistant entries in `~/.claude/projects/**/*.jsonl`, inside the optional time filter; nested `usage.iterations` is ignored to avoid double counting.")
    lines.append("- Codex: sums unique cumulative `event_msg.payload.info.total_token_usage` deltas from `~/.codex/sessions` and `~/.codex/archived_sessions`; repeated `token_count` rows are deduplicated. Without a time filter this is equivalent to the final cumulative session total for monotonic sessions.")
    lines.append("- Project matching uses session path, `cwd`, parent session path, and Codex git repository metadata. Conversation text is not used for matching or output.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- `summary.json`: machine-readable aggregate.")
    lines.append(f"- `sessions.csv`: per matched session file.")
    lines.append(f"- `by_tool.csv`, `by_model.csv`, `by_month.csv`: aggregate tables.")
    lines.append("")
    lines.append("## Caveat")
    lines.append("")
    lines.append("Use observed context tokens when describing the total amount of model context processed by agent tools. Use cache-excluded tokens only when explicitly discussing non-cached/fresh work; it will be much smaller for long agent-heavy projects.")
    lines.append("The USD figure is a token-price equivalent, not necessarily actual out-of-pocket spend, because Claude Code/Codex may be paid through subscriptions or bundled plans. Update the price table if better historical rates are available.")
    lines.append("")
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"- Project root: `{args.project_root}`")
    lines.append(f"- Project name: `{args.project_name}`")
    lines.append(f"- Pi root: `{args.pi_root}`")
    lines.append(f"- Claude projects root: `{args.claude_projects_root}`")
    lines.append(f"- Codex roots: `{', '.join(str(root) for root in args.codex_roots)}`")
    lines.append(f"- Price table: `{args.price_table}`")
    lines.append(f"- Since: `{args.since or ''}`")
    lines.append(f"- Until: `{args.until or ''}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    home = Path.home()
    parser = argparse.ArgumentParser(
        description="Summarize local Pi/Claude Code/Codex token usage for Kratt-related sessions."
    )
    parser.add_argument("--project-root", type=Path, default=repo_root, help="Project root used for cwd/path matching. Default: repo root inferred from this script.")
    parser.add_argument("--project-name", default="kratt", help="Project name marker used for encoded session paths. Default: kratt.")
    parser.add_argument("--repo-owner", default="Yikizi", help="Repository owner marker for Codex git metadata. Default: Yikizi.")
    parser.add_argument("--pi-root", type=Path, default=home / ".pi" / "agent" / "sessions", help="Pi session root.")
    parser.add_argument("--claude-projects-root", type=Path, default=home / ".claude" / "projects", help="Claude Code projects transcript root.")
    parser.add_argument(
        "--codex-roots",
        type=Path,
        nargs="*",
        default=[home / ".codex" / "sessions", home / ".codex" / "archived_sessions"],
        help="Codex session roots. Defaults to current and archived Codex sessions.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("output") / "agent-token-usage", help="Output directory for summary files.")
    parser.add_argument("--prefix", default="agent_token_usage", help="Output filename prefix. Default: agent_token_usage.")
    parser.add_argument("--price-table", type=Path, default=repo_root / "tools" / "analysis" / "agent_token_prices.json", help="JSON price table for token-equivalent USD estimates.")
    parser.add_argument("--since", help="Only count usage events at or after this ISO timestamp/date. Naive timestamps are treated as UTC.")
    parser.add_argument("--until", help="Only count usage events at or before this ISO timestamp/date. Naive timestamps are treated as UTC.")
    parser.add_argument("--tools", nargs="*", choices=["pi", "claude_code", "codex"], default=["pi", "claude_code", "codex"], help="Tools to scan. Default: all.")
    parser.add_argument("--no-write", action="store_true", help="Print summary to stdout only; do not write files.")
    return parser.parse_args(list(argv))


def build_summary(args: argparse.Namespace) -> Tuple[ScanResult, Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    price_entries, price_metadata = load_price_entries(args.price_table.expanduser())
    ctx = MatchContext(
        project_root=args.project_root.expanduser().resolve(),
        project_name=args.project_name,
        repo_owner=args.repo_owner,
        price_entries=price_entries,
        since=parse_filter_time(args.since),
        until=parse_filter_time(args.until),
    )
    result = ScanResult()
    tools = set(args.tools)
    if "pi" in tools:
        scan_pi_sessions(args.pi_root.expanduser(), ctx, result)
    if "claude_code" in tools:
        scan_claude_projects(args.claude_projects_root.expanduser(), ctx, result)
    if "codex" in tools:
        scan_codex_sessions([root.expanduser() for root in args.codex_roots], ctx, result)

    session_rows = [record.to_row() for record in sorted(result.records, key=lambda record: (record.tool, record.session_file))]
    by_tool = aggregate_rows_to_dicts(result.by_tool, ["tool"])
    by_model = aggregate_rows_to_dicts(result.by_model, ["tool", "provider", "model"])
    by_month = aggregate_rows_to_dicts(result.by_month, ["month", "tool"])
    summary = {
        "schema_version": SCHEMA_VERSION,
        "project_root": str(ctx.project_root),
        "project_name": ctx.project_name,
        "repo_owner": ctx.repo_owner,
        "totals": totals_with_counters(result.records),
        "roots": {
            "pi": str(args.pi_root.expanduser()),
            "claude_projects": str(args.claude_projects_root.expanduser()),
            "codex": [str(root.expanduser()) for root in args.codex_roots],
        },
        "price_table": price_metadata,
        "time_filter": {
            "since": iso_or_empty(ctx.since),
            "until": iso_or_empty(ctx.until),
        },
        "parser_rules": {
            "pi": "sum assistant message.usage entries inside the optional time filter",
            "claude_code": "sum assistant message.usage top-level counters inside the optional time filter; ignore nested iterations",
            "codex": "sum unique cumulative token_count deltas inside the optional time filter; repeated cumulative values are deduplicated",
        },
    }
    return result, summary, session_rows, by_tool, by_model, by_month


def write_outputs(args: argparse.Namespace, summary: Dict[str, Any], session_rows: Sequence[Dict[str, Any]], by_tool: Sequence[Dict[str, Any]], by_model: Sequence[Dict[str, Any]], by_month: Sequence[Dict[str, Any]]) -> Dict[str, str]:
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": output_dir / f"{args.prefix}_summary.json",
        "summary_md": output_dir / f"{args.prefix}_summary.md",
        "sessions_csv": output_dir / f"{args.prefix}_sessions.csv",
        "by_tool_csv": output_dir / f"{args.prefix}_by_tool.csv",
        "by_model_csv": output_dir / f"{args.prefix}_by_model.csv",
        "by_month_csv": output_dir / f"{args.prefix}_by_month.csv",
    }
    write_json(paths["summary_json"], {**summary, "by_tool": list(by_tool), "by_model": list(by_model), "by_month": list(by_month)})
    write_markdown(paths["summary_md"], summary=summary, by_tool=by_tool, by_model=by_model, by_month=by_month, args=args)
    write_csv(paths["sessions_csv"], session_rows)
    write_csv(paths["by_tool_csv"], by_tool)
    write_csv(paths["by_model_csv"], by_model)
    write_csv(paths["by_month_csv"], by_month)
    return {key: str(value) for key, value in paths.items()}


def print_stdout_summary(summary: Dict[str, Any], by_tool: Sequence[Dict[str, Any]], paths: Optional[Dict[str, str]] = None) -> None:
    totals = summary["totals"]
    print("Kratt agent token usage")
    print(f"  sessions: {totals['sessions']}")
    print(f"  observed_context_tokens: {fmt_int(totals['observed_context_tokens'])}")
    print(f"  cache_read_tokens:       {fmt_int(totals['cache_read_tokens'])}")
    print(f"  cache_excluded_tokens:   {fmt_int(totals['cache_excluded_tokens'])}")
    print(f"  fresh_input_tokens:      {fmt_int(totals['fresh_input_tokens'])}")
    print(f"  output_tokens:           {fmt_int(totals['output_tokens'])}")
    print(f"  estimated_cost_usd:      {fmt_usd(float(totals['estimated_cost_usd']))}")
    print(f"  logged_cost_usd:         {fmt_usd(float(totals['logged_cost_usd']))}")
    print("\nBy tool:")
    for row in sorted(by_tool, key=lambda item: item["observed_context_tokens"], reverse=True):
        print(
            f"  {row['tool']}: sessions={row['sessions']} "
            f"observed={fmt_int(row['observed_context_tokens'])} "
            f"cache_read={fmt_int(row['cache_read_tokens'])} "
            f"cache_excluded={fmt_int(row['cache_excluded_tokens'])} "
            f"est_cost={fmt_usd(float(row['estimated_cost_usd']))}"
        )
    if paths:
        print("\nWrote:")
        for path in paths.values():
            print(f"  {path}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    _result, summary, session_rows, by_tool, by_model, by_month = build_summary(args)
    paths: Optional[Dict[str, str]] = None
    if not args.no_write:
        paths = write_outputs(args, summary, session_rows, by_tool, by_model, by_month)
    print_stdout_summary(summary, by_tool, paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
