#!/usr/bin/env python3
"""Benchmark multiple local LLMs on Estonian Kratt commands.

Tests JSON validity, intent correctness, response quality, and latency for
each candidate model on a fixed set of representative Estonian utterances.

Models are pulled via Ollama. Skip any model not installed (warns but continues).

Usage:
    python bench_estonian_llms.py
    python bench_estonian_llms.py --models gemma3:12b qwen2.5:14b
    python bench_estonian_llms.py --output results.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

# Same system prompt as production pipeline so results transfer directly
SYSTEM_PROMPT = """\
Sa oled Kratt, eestikeelne häälassistent. Juhi nutiseadmeid kasutaja käskude järgi.

Saadaolevad toimingud (vasta AINULT JSON-iga):
- {"action":"turn_on","entity_id":"...","color":"värv"}
- {"action":"turn_off","entity_id":"..."}
- {"action":"set_color","entity_id":"...","color":"värv"}
- {"action":"set_brightness","entity_id":"...","brightness":0-255}
- {"action":"get_state","entity_id":"..."}

Seadmed:
- light.elutuba — Elutoa lamp (RGB, heledus)
- light.magamistuba — Magamistoa lamp (RGB, heledus)
- switch.kohvimasin — Kohvimasin (sees/väljas)
- sensor.temperatuur — Toa temperatuuri andur
- sensor.kellaaeg — Praegune kellaaeg

Vasta: {"actions":[...],"response":"lühike eestikeelne vastus"}
Kui tuba pole täpsustatud, kasuta elutuba. Vastus olgu lühike (TTS).
"""


@dataclass
class TestCase:
    id: str
    utterance: str
    # What we expect to see in the parsed actions
    expected_action: str
    expected_entity: str | None = None
    # Soft check: substrings that should appear somewhere in the response
    expected_response_keywords: list[str] = field(default_factory=list)


# Representative test set drawn from the existing test_loop.py validation
TEST_CASES = [
    TestCase(
        id="T01_turn_on_simple",
        utterance="lülita tuli põlema",
        expected_action="turn_on",
        expected_entity="light.elutuba",
    ),
    TestCase(
        id="T02_color",
        utterance="tee tuli punaseks",
        expected_action="set_color",
        expected_entity="light.elutuba",
    ),
    TestCase(
        id="T03_get_temp",
        utterance="kui soe toas on",
        expected_action="get_state",
        expected_entity="sensor.temperatuur",
    ),
    TestCase(
        id="T04_get_time",
        utterance="mis kell on",
        expected_action="get_state",
        expected_entity="sensor.kellaaeg",
    ),
    TestCase(
        id="T05_specific_room",
        utterance="pane magamistoa lamp kinni",
        expected_action="turn_off",
        expected_entity="light.magamistuba",
    ),
    TestCase(
        id="T06_brightness_implicit",
        utterance="tee elutoas hämar",
        expected_action="set_brightness",
        expected_entity="light.elutuba",
    ),
    TestCase(
        id="T07_context_inference",
        utterance="elutoas on liiga pime",
        expected_action="turn_on",
        expected_entity="light.elutuba",
    ),
    TestCase(
        id="T08_multi_action",
        utterance="pane kohv käima ja elutoa tuli põlema",
        expected_action="turn_on",  # at least one of the actions
        expected_entity=None,  # don't constrain entity for multi-action
    ),
]


@dataclass
class CaseResult:
    case_id: str
    utterance: str
    success: bool  # JSON parsed AND expected action present
    json_valid: bool
    action_match: bool
    entity_match: bool | None  # None if no expectation
    actions: list[dict]
    response: str
    latency_s: float
    error: str | None = None


@dataclass
class ModelResult:
    model: str
    cases: list[CaseResult]
    available: bool = True
    error: str | None = None

    @property
    def success_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for c in self.cases if c.success) / len(self.cases)

    @property
    def json_valid_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for c in self.cases if c.json_valid) / len(self.cases)

    @property
    def median_latency_s(self) -> float:
        latencies = [c.latency_s for c in self.cases if c.json_valid]
        return statistics.median(latencies) if latencies else 0.0


def query_model(model: str, utterance: str, timeout: int = 60) -> tuple[dict | None, float, str | None]:
    """Send one Estonian utterance to a model. Returns (parsed_json, latency, error)."""
    t0 = time.monotonic()
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": utterance},
                ],
            },
            timeout=timeout,
        )
        latency = time.monotonic() - t0
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        try:
            parsed = json.loads(content)
            return parsed, latency, None
        except json.JSONDecodeError as e:
            return None, latency, f"JSON parse: {e}; raw={content[:200]}"
    except Exception as e:
        return None, time.monotonic() - t0, str(e)


def evaluate_case(case: TestCase, parsed: dict | None) -> tuple[bool, bool, bool | None]:
    """Returns (action_match, entity_match, _)."""
    if not parsed or "actions" not in parsed:
        return False, False if case.expected_entity else None, None

    actions = parsed.get("actions", [])
    if not isinstance(actions, list):
        return False, False if case.expected_entity else None, None

    action_names = [a.get("action") for a in actions if isinstance(a, dict)]
    action_match = case.expected_action in action_names

    entity_match: bool | None = None
    if case.expected_entity is not None:
        entities = [a.get("entity_id") for a in actions if isinstance(a, dict)]
        entity_match = case.expected_entity in entities

    return action_match, entity_match, None


def warmup_model(model: str) -> bool:
    """Send a trivial prompt to load model into memory and cache system prompt."""
    print(f"  warming up...", end=" ", flush=True)
    parsed, latency, err = query_model(model, "tere", timeout=300)
    if err:
        print(f"FAILED ({err[:100]})")
        return False
    print(f"OK ({latency:.1f}s)")
    return True


def run_model(model: str, cases: list[TestCase]) -> ModelResult:
    print(f"\n=== {model} ===")
    if not warmup_model(model):
        return ModelResult(model=model, cases=[], available=False, error="warmup failed")

    case_results: list[CaseResult] = []
    for case in cases:
        parsed, latency, err = query_model(model, case.utterance)
        json_valid = parsed is not None
        action_match, entity_match, _ = evaluate_case(case, parsed)
        success = json_valid and action_match and (entity_match is not False)

        result = CaseResult(
            case_id=case.id,
            utterance=case.utterance,
            success=success,
            json_valid=json_valid,
            action_match=action_match,
            entity_match=entity_match,
            actions=parsed.get("actions", []) if parsed else [],
            response=parsed.get("response", "") if parsed else "",
            latency_s=round(latency, 2),
            error=err,
        )
        case_results.append(result)

        mark = "✓" if success else "✗"
        print(f"  {mark} {case.id} ({latency:.1f}s)  \"{case.utterance}\"")
        if parsed:
            print(f"     → {json.dumps(parsed.get('actions', []), ensure_ascii=False)}")
            if parsed.get('response'):
                print(f"     ↳ \"{parsed['response']}\"")
        if err:
            print(f"     ERR: {err[:200]}")

    return ModelResult(model=model, cases=case_results)


def print_summary(results: list[ModelResult]):
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Model':<35} {'Success':>10} {'JSON':>8} {'Median LLM':>14}")
    print("-" * 80)
    for r in results:
        if not r.available:
            print(f"{r.model:<35} {'N/A':>10} {'N/A':>8} {'N/A':>14}  ({r.error})")
            continue
        print(
            f"{r.model:<35} "
            f"{r.success_rate * 100:>9.0f}% "
            f"{r.json_valid_rate * 100:>7.0f}% "
            f"{r.median_latency_s:>13.1f}s"
        )


DEFAULT_MODELS = [
    "gemma3:12b",
    "gemma3:27b",
    "qwen2.5:14b",
    "alibayram/erurollm-9b-instruct",
]


def main():
    parser = argparse.ArgumentParser(description="Benchmark Estonian LLMs for Kratt")
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="Ollama model tags to test",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write full JSON results",
    )
    args = parser.parse_args()

    # Verify ollama is up
    try:
        requests.get("http://localhost:11434/", timeout=2)
    except Exception:
        print("ERROR: Ollama is not reachable at http://localhost:11434/")
        print("Run: ollama serve")
        sys.exit(1)

    results = [run_model(model, TEST_CASES) for model in args.models]
    print_summary(results)

    if args.output:
        payload = {
            "test_cases": [asdict(c) for c in TEST_CASES],
            "results": [
                {
                    "model": r.model,
                    "available": r.available,
                    "error": r.error,
                    "success_rate": r.success_rate,
                    "json_valid_rate": r.json_valid_rate,
                    "median_latency_s": r.median_latency_s,
                    "cases": [asdict(c) for c in r.cases],
                }
                for r in results
            ],
        }
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"\nFull results: {args.output}")


if __name__ == "__main__":
    main()
