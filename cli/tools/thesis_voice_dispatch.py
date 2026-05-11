#!/usr/bin/env python3
"""Voice-to-agent dispatcher for thesis correction requests."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
STT_DIR = REPO_ROOT / "stt-integration" / "kiirkirjutaja-source"
CONFIG_PATH = Path(
    os.environ.get(
        "KRATT_THESIS_VOICE_CONFIG",
        REPO_ROOT / "cli" / "tools" / "thesis_voice_dispatch.config.json",
    )
)
DEFAULT_TARGET = os.environ.get("KRATT_THESIS_AGENT_TMUX_TARGET", "kratt-thesis-agent:0.0")
DEFAULT_WORKER_SESSION = os.environ.get(
    "KRATT_THESIS_WORKER_TMUX_SESSION",
    "kratt-thesis-voice-workers",
)
DEFAULT_SUBMIT_KEY = os.environ.get("KRATT_THESIS_VOICE_SUBMIT_KEY", "Enter")
DEFAULT_INPUT_METHOD = os.environ.get("KRATT_THESIS_VOICE_INPUT_METHOD", "paste")
DEFAULT_SUBMIT_DELAY_MS = int(os.environ.get("KRATT_THESIS_VOICE_SUBMIT_DELAY_MS", "75"))
DEFAULT_PURPOSE = os.environ.get("KRATT_VOICE_PURPOSE", "thesis")
DEFAULT_TTS_URL = os.environ.get("KRATT_VOICE_TTS_URL", "http://127.0.0.1:5380/synthesize")
DEFAULT_TTS_SPEAKER = os.environ.get("KRATT_VOICE_TTS_SPEAKER", "meelis")
DEFAULT_TTS_SPEED = float(os.environ.get("KRATT_VOICE_TTS_SPEED", "1.0"))

DEFAULT_CONFIG = {
    "default_profile": "claude-yolo",
    "control_words": {
        "escape": ["stop", "stopp"],
    },
    "profiles": {
        "claude-yolo": {
            "kind": "claude",
            "yolo": True,
            "model": None,
            "max_budget_usd": "1.25",
        },
        "codex-yolo": {
            "kind": "codex",
            "yolo": True,
            "model": None,
        },
    },
}


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def require_cmd(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"missing required command: {name}")


def load_config() -> dict:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            local_config = json.load(handle)
        config["default_profile"] = local_config.get(
            "default_profile",
            config["default_profile"],
        )
        if "control_words" in local_config:
            config["control_words"] = local_config["control_words"]
        config["profiles"].update(local_config.get("profiles", {}))
    return config


def resolve_profile(args: argparse.Namespace) -> dict:
    config = load_config()
    profile_name = args.profile or config.get("default_profile") or "claude-yolo"
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles)) or "(none)"
        raise SystemExit(f"unknown profile '{profile_name}'. Available profiles: {available}")

    profile = dict(profiles[profile_name])
    profile["name"] = profile_name
    if getattr(args, "agent", None):
        profile["kind"] = args.agent
    if getattr(args, "model", None):
        profile["model"] = args.model
    if getattr(args, "yolo", None) is not None:
        profile["yolo"] = args.yolo
    if getattr(args, "max_budget_usd", None):
        profile["max_budget_usd"] = args.max_budget_usd
    return profile


def render_template(template: str, *, prompt: str, prompt_path: Optional[str], profile: dict) -> str:
    values = {
        "repo": str(REPO_ROOT),
        "prompt": prompt,
        "prompt_q": shlex.quote(prompt),
        "prompt_path": prompt_path or "",
        "prompt_path_q": shlex.quote(prompt_path or ""),
        "model": profile.get("model") or "",
        "model_q": shlex.quote(profile.get("model") or ""),
        "max_budget_usd": str(profile.get("max_budget_usd") or "1.25"),
    }
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def claude_interactive_command(prompt: str, profile: dict) -> str:
    parts = ["claude"]
    if profile.get("yolo", True):
        parts.append("--dangerously-skip-permissions")
    if profile.get("model"):
        parts.extend(["--model", str(profile["model"])])
    parts.append(prompt)
    return " ".join(shlex.quote(part) for part in parts)


def claude_worker_command(prompt_path: str, profile: dict) -> str:
    parts = ["claude", "-p"]
    if profile.get("yolo", True):
        parts.append("--dangerously-skip-permissions")
    if profile.get("model"):
        parts.extend(["--model", str(profile["model"])])
    if profile.get("max_budget_usd"):
        parts.extend(["--max-budget-usd", str(profile["max_budget_usd"])])
    return " ".join(shlex.quote(part) for part in parts) + f" < {shlex.quote(prompt_path)}"


def codex_interactive_command(prompt: str, profile: dict) -> str:
    parts = ["codex", "--no-alt-screen"]
    if profile.get("yolo", True):
        parts.extend(["-s", "danger-full-access", "--dangerously-bypass-approvals-and-sandbox"])
    if profile.get("model"):
        parts.extend(["-m", str(profile["model"])])
    parts.append(prompt)
    return " ".join(shlex.quote(part) for part in parts)


def codex_worker_command(prompt_path: str, profile: dict) -> str:
    parts = ["codex", "exec", "-C", str(REPO_ROOT)]
    if profile.get("yolo", True):
        parts.extend(["-s", "danger-full-access", "--dangerously-bypass-approvals-and-sandbox"])
    if profile.get("model"):
        parts.extend(["-m", str(profile["model"])])
    parts.append("-")
    return " ".join(shlex.quote(part) for part in parts) + f" < {shlex.quote(prompt_path)}"


def build_agent_command(profile: dict, *, prompt: str, prompt_path: Optional[str] = None, worker: bool = False) -> str:
    kind = profile.get("kind", "claude")
    if kind == "claude":
        require_cmd("claude")
        return claude_worker_command(prompt_path or "", profile) if worker else claude_interactive_command(prompt, profile)
    if kind == "codex":
        require_cmd("codex")
        return codex_worker_command(prompt_path or "", profile) if worker else codex_interactive_command(prompt, profile)
    if kind == "shell":
        template_key = "worker_command" if worker else "dispatcher_command"
        template = profile.get(template_key)
        if not template:
            raise SystemExit(f"profile '{profile['name']}' is kind=shell but lacks {template_key}")
        return render_template(template, prompt=prompt, prompt_path=prompt_path, profile=profile)
    raise SystemExit(f"unsupported profile kind '{kind}' in profile '{profile['name']}'")


def add_profile_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        help=f"Agent profile from {CONFIG_PATH} (default: config default_profile)",
    )
    parser.add_argument(
        "--agent",
        choices=["claude", "codex", "shell"],
        help="Override profile kind for this command",
    )
    parser.add_argument("--model", help="Override profile model for this command")
    yolo_group = parser.add_mutually_exclusive_group()
    yolo_group.add_argument("--yolo", dest="yolo", action="store_true", default=None)
    yolo_group.add_argument("--no-yolo", dest="yolo", action="store_false")


def list_profiles(_: argparse.Namespace) -> None:
    config = load_config()
    default_profile = config.get("default_profile")
    for name, profile in sorted(config.get("profiles", {}).items()):
        marker = "*" if name == default_profile else " "
        model = profile.get("model") or "default"
        yolo = "yolo" if profile.get("yolo", False) else "guarded"
        kind = profile.get("kind", "claude")
        print(f"{marker} {name:16s} kind={kind:6s} model={model} mode={yolo}")


def tmux_has_session(session: str) -> bool:
    return subprocess.run(
        ["tmux", "has-session", "-t", session],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def tmux_send_text(
    target: str,
    text: str,
    submit_key: Optional[str] = DEFAULT_SUBMIT_KEY,
    input_method: str = DEFAULT_INPUT_METHOD,
    submit_delay_ms: int = DEFAULT_SUBMIT_DELAY_MS,
) -> None:
    require_cmd("tmux")
    if input_method == "type":
        run(["tmux", "send-keys", "-t", target, "-l", text])
        if submit_key:
            if submit_delay_ms > 0:
                time.sleep(submit_delay_ms / 1000)
            run(["tmux", "send-keys", "-t", target, submit_key])
        return

    buffer_name = f"kratt-thesis-voice-{os.getpid()}"
    run(["tmux", "set-buffer", "-b", buffer_name, text])
    try:
        run(["tmux", "paste-buffer", "-t", target, "-b", buffer_name])
        if submit_key:
            if submit_delay_ms > 0:
                time.sleep(submit_delay_ms / 1000)
            run(["tmux", "send-keys", "-t", target, submit_key])
    finally:
        subprocess.run(
            ["tmux", "delete-buffer", "-b", buffer_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


def tmux_send_escape(target: str) -> None:
    require_cmd("tmux")
    run(["tmux", "send-keys", "-t", target, "Escape"])


def choose_audio_player(explicit: Optional[str] = None) -> Optional[list[str]]:
    if explicit:
        return shlex.split(explicit)
    for candidate in ("paplay", "play", "aplay", "termux-media-player"):
        path = shutil.which(candidate)
        if path:
            if candidate == "play":
                return [path, "-q"]
            if candidate == "termux-media-player":
                return [path, "play"]
            return [path]
    return None


def speak_text(
    text: str,
    *,
    tts_url: str = DEFAULT_TTS_URL,
    speaker: str = DEFAULT_TTS_SPEAKER,
    speed: float = DEFAULT_TTS_SPEED,
    player: Optional[str] = None,
) -> None:
    payload = json.dumps({"text": text, "speaker": speaker, "speed": speed}).encode("utf-8")
    request = urllib.request.Request(
        tts_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            audio = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"tts failed: {exc}", file=sys.stderr)
        return

    player_cmd = choose_audio_player(player)
    if not player_cmd:
        print("tts audio ready, but no player found (paplay/play/aplay/termux-media-player)", file=sys.stderr)
        return

    suffix = ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as wav_file:
        wav_file.write(audio)
        wav_path = wav_file.name
    try:
        subprocess.run([*player_cmd, wav_path], check=False)
    finally:
        try:
            os.unlink(wav_path)
        except OSError:
            pass


def normalize_control_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"^[^\wõäöüšž]+|[^\wõäöüšž]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def control_action_for_transcript(transcript: str) -> Optional[str]:
    config = load_config()
    normalized = normalize_control_text(transcript)
    for action, words in config.get("control_words", {}).items():
        normalized_words = {normalize_control_text(word) for word in words}
        if normalized in normalized_words:
            return action
    return None


def dispatcher_prompt(transcript: str, purpose: str = DEFAULT_PURPOSE) -> str:
    if purpose == "dev":
        return textwrap.dedent(
            f"""\
            Voice-dispatched Kratt development request.

            Transcript:
            {transcript.strip()}

            Dispatcher rules:
            - Treat this as a coding/development request from Mattias for the Kratt repo.
            - Preserve existing user changes: inspect git status before editing and do not revert unrelated work.
            - Keep the request bounded. Prefer the smallest safe implementation and avoid broad refactors.
            - Use repo guardrails from AGENTS.md / CLAUDE.md, especially thesis-deadline scope control.
            - If the task is independent and your environment supports workers/subagents, delegate one bounded worker and keep this pane responsive.
            - When done, report changed files and any verification command you ran.
            """
        ).strip()

    return textwrap.dedent(
        f"""\
        Voice-dispatched thesis correction request.

        Transcript:
        {transcript.strip()}

        Dispatcher rules:
        - Treat this as a small thesis-document correction request from Mattias.
        - Keep the parent session available for more voice prompts. Immediately delegate the actual investigation/edit to one bounded background subagent, background agent, or worker if your environment supports it.
        - Do not spend a long parent-session turn doing the edit yourself unless background delegation is unavailable.
        - If no subagent mechanism is available, do only the smallest safe edit yourself and report that fallback explicitly.
        - If the request names a PDF page, map it to the LaTeX source under docs/thesis/thesis-tex-estonian before editing.
        - Thesis prose is Estonian. Replace English filler with correct Estonian, not literal calques.
        - Scope is one fix. No broad cleanup, no generated artifacts, no unrelated refactors.
        - Preserve existing user changes: inspect git status before editing and do not revert unrelated work.
        - When done, report changed files and any verification command you ran.
        """
    ).strip()


def worker_prompt(transcript: str, purpose: str = DEFAULT_PURPOSE) -> str:
    if purpose == "dev":
        return textwrap.dedent(
            f"""\
            You are a voice-dispatched Kratt coding worker.

            User transcript:
            {transcript.strip()}

            Task:
            - Make the small development change requested by the transcript.
            - Inspect git status before editing, preserve unrelated user changes, and follow AGENTS.md / CLAUDE.md.
            - Keep scope tight because the thesis deadline is near; do not start long training jobs or broad refactors.
            - Prefer targeted edits and run the smallest relevant verification.
            - Finish with changed files and verification.
            """
        ).strip()

    return textwrap.dedent(
        f"""\
        You are a voice-dispatched Kratt thesis editing worker.

        User transcript:
        {transcript.strip()}

        Task:
        - Make exactly one small thesis-document correction requested by the transcript.
        - If a PDF page is named, map it to the LaTeX source under docs/thesis/thesis-tex-estonian first.
        - Thesis prose is Estonian; prefer idiomatic Estonian.
        - Inspect git status before editing, preserve unrelated user changes, and do not run broad cleanup.
        - Do not regenerate thesis PDFs unless it is necessary to verify this exact correction.
        - Finish with changed files and verification.
        """
    ).strip()


def start_agent(args: argparse.Namespace) -> None:
    require_cmd("tmux")
    profile = resolve_profile(args)

    session = args.session
    if tmux_has_session(session):
        print(f"dispatcher agent already running: {session}")
        print(f"attach: tmux attach -t {session}")
        return

    initial_prompt = textwrap.dedent(
        """\
        You are the Kratt thesis voice dispatcher.

        Stay responsive. For every incoming voice-dispatched thesis correction:
        - Immediately delegate the concrete investigation/edit to a background
          agent, background subagent, or worker when your environment supports it.
        - Keep the parent dispatcher free for the next voice prompt; do not spend a
          long turn doing the edit in this parent session.
        - If no background delegation mechanism exists, say so and do only the
          smallest safe fallback yourself.
        - Keep each request scoped to one correction, preserve existing user
          changes, and report only changed files plus verification.
        """
    ).strip()
    agent_command = build_agent_command(profile, prompt=initial_prompt)
    command = f"cd {shlex.quote(str(REPO_ROOT))} && {agent_command}"

    run(["tmux", "new-session", "-d", "-s", session, "-n", "dispatcher", command])
    print(f"started dispatcher agent: {session} ({profile['name']}, kind={profile.get('kind')}, model={profile.get('model') or 'default'})")
    print(f"attach: tmux attach -t {session}")
    print(f"default send target: {session}:0.0")


def start_blank_pane(args: argparse.Namespace) -> None:
    require_cmd("tmux")
    session = args.session
    if tmux_has_session(session):
        print(f"tmux session already running: {session}")
        print(f"attach: tmux attach -t {session}")
        print(f"default send target: {session}:0.0")
        return

    command = f"cd {shlex.quote(str(REPO_ROOT))} && exec $SHELL -l"
    run(["tmux", "new-session", "-d", "-s", session, "-n", "voice-target", command])
    print(f"started blank tmux target: {session}")
    print(f"attach: tmux attach -t {session}")
    print(f"start any agent there, then dispatch with target {session}:0.0")


def dispatch_to_worker(args: argparse.Namespace, transcript: str) -> None:
    require_cmd("tmux")
    profile = resolve_profile(args)

    prompt = worker_prompt(transcript, args.purpose)
    now = datetime.now().strftime("%H%M%S")
    window_name = f"voice-{now}"
    prompt_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="kratt-thesis-voice-",
        suffix=".prompt.md",
        delete=False,
    )
    with prompt_file:
        prompt_file.write(prompt)
        prompt_path = prompt_file.name

    if not tmux_has_session(args.session):
        run(
            [
                "tmux",
                "new-session",
                "-d",
                "-s",
                args.session,
                "-n",
                "workers",
                f"cd {shlex.quote(str(REPO_ROOT))} && exec $SHELL -l",
            ]
        )

    agent_cmd = build_agent_command(
        profile,
        prompt=prompt,
        prompt_path=prompt_path,
        worker=True,
    )
    worker_label = (
        f"profile={profile['name']} "
        f"kind={profile.get('kind')} "
        f"model={profile.get('model') or 'default'}"
    )

    command = (
        f"cd {shlex.quote(str(REPO_ROOT))} && "
        "echo '[kratt thesis-voice] worker prompt:' && "
        f"sed -n '1,80p' {shlex.quote(prompt_path)} && "
        f"echo && echo {shlex.quote('[kratt thesis-voice] starting worker ' + worker_label)} && "
        f"{agent_cmd}; "
        "rc=$?; echo; "
        "echo \"[kratt thesis-voice] worker exited rc=$rc\"; "
        "exec $SHELL -l"
    )
    run(["tmux", "new-window", "-t", args.session, "-n", window_name, command])
    print(f"dispatched worker: {args.session}:{window_name} ({profile['name']}, kind={profile.get('kind')}, model={profile.get('model') or 'default'})")
    print(f"attach: tmux attach -t {args.session}")


def dispatch_text(args: argparse.Namespace, transcript: str) -> None:
    control_action = control_action_for_transcript(transcript)
    if args.dry_run:
        if control_action == "escape":
            print("<Escape>")
            return
        if args.mode == "raw-pane":
            print(transcript)
        else:
            prompt = worker_prompt(transcript, args.purpose) if args.mode == "worker-window" else dispatcher_prompt(transcript, args.purpose)
            print(prompt)
        return

    if control_action == "escape":
        tmux_send_escape(args.target)
        print(f"sent Escape to tmux target: {args.target}")
        return

    if args.mode == "worker-window":
        dispatch_to_worker(args, transcript)
        if getattr(args, "speak_dispatch", False):
            speak_text(args.speak_text, tts_url=args.tts_url, speaker=args.tts_speaker, speed=args.tts_speed, player=args.tts_player)
        return

    target = args.target
    prompt = transcript if args.mode == "raw-pane" else dispatcher_prompt(transcript, args.purpose)
    submit_key = None if args.no_enter else args.submit_key
    tmux_send_text(
        target,
        prompt,
        submit_key=submit_key,
        input_method=args.input_method,
        submit_delay_ms=args.submit_delay_ms,
    )
    suffix = "" if submit_key is None else f" with submit key {submit_key}"
    suffix += f" via {args.input_method} after {args.submit_delay_ms}ms"
    print(f"sent transcript to tmux target: {target}{suffix}")
    if getattr(args, "speak_dispatch", False):
        speak_text(args.speak_text, tts_url=args.tts_url, speaker=args.tts_speaker, speed=args.tts_speed, player=args.tts_player)


def list_devices() -> None:
    require_cmd("ffmpeg")
    proc = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    in_audio = False
    for line in proc.stdout.splitlines():
        if "AVFoundation audio devices:" in line:
            in_audio = True
        if "AVFoundation video devices:" in line:
            in_audio = False
        if in_audio and "Error opening" not in line and "in#0" not in line:
            print(line)


ASR_SCRIPT = r"""
import sys
import numpy as np
import sherpa_onnx

SAMPLE_RATE = 16000
CHUNK = 1600

rec = sherpa_onnx.OnlineRecognizer.from_transducer(
    tokens="models/sherpa-int8/tokens.txt",
    encoder="models/sherpa-int8/encoder.int8.onnx",
    decoder="models/sherpa-int8/decoder.int8.onnx",
    joiner="models/sherpa-int8/joiner.int8.onnx",
    num_threads=2,
    sample_rate=SAMPLE_RATE,
    feature_dim=80,
    enable_endpoint_detection=True,
    rule1_min_trailing_silence=2.4,
    rule2_min_trailing_silence=1.2,
    rule3_min_utterance_length=300,
)

stream = rec.create_stream()
last = ""
print("Listening...", file=sys.stderr, flush=True)

while True:
    b = sys.stdin.buffer.read(CHUNK * 2)
    if not b or len(b) < CHUNK * 2:
        break

    samples = np.frombuffer(b, dtype=np.int16).astype(np.float32) / 32768.0
    stream.accept_waveform(SAMPLE_RATE, samples)

    while rec.is_ready(stream):
        rec.decode_stream(stream)

    text = rec.get_result(stream).strip()
    endpoint = rec.is_endpoint(stream)

    if text and text != last:
        print("PARTIAL\t" + text, flush=True)
        last = text

    if endpoint and text:
        print("FINAL\t" + text, flush=True)
        rec.reset(stream)
        last = ""
"""


def ensure_image(args: argparse.Namespace) -> None:
    require_cmd("docker")
    if args.no_build:
        return
    print(f"building Kiirkirjutaja image: {args.image}", file=sys.stderr)
    run(["docker", "build", "-t", args.image, "."], cwd=STT_DIR)


def listen(args: argparse.Namespace) -> None:
    require_cmd("ffmpeg")
    require_cmd("docker")
    ensure_image(args)

    device = args.device
    if args.list_devices:
        list_devices()
        return
    if not device:
        list_devices()
        raise SystemExit("choose a microphone with --device <id>, for example --device 1")
    if not device.startswith(":"):
        device = f":{device}"

    ffmpeg_cmd = [
        "ffmpeg",
        "-f",
        "avfoundation",
        "-i",
        device,
        "-ar",
        "16000",
        "-ac",
        "1",
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "-loglevel",
        "error",
        "-",
    ]
    docker_cmd = ["docker", "run", "--rm", "-i", args.image, "python", "-u", "-c", ASR_SCRIPT]

    print("listening; press Ctrl+C to stop", file=sys.stderr)
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)
    docker_proc = subprocess.Popen(
        docker_cmd,
        stdin=ffmpeg_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=1,
    )
    assert ffmpeg_proc.stdout is not None
    ffmpeg_proc.stdout.close()

    try:
        assert docker_proc.stdout is not None
        for raw_line in docker_proc.stdout:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            kind, _, text = line.partition("\t")
            if kind == "PARTIAL" and args.show_partial:
                print(f"partial: {text}", file=sys.stderr)
            elif kind == "FINAL" and text:
                print(f"final: {text}", file=sys.stderr)
                dispatch_text(args, text)
    except KeyboardInterrupt:
        pass
    finally:
        docker_proc.terminate()
        ffmpeg_proc.terminate()
        docker_proc.wait(timeout=5)
        ffmpeg_proc.wait(timeout=5)


def add_voice_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--purpose", choices=["thesis", "dev"], default=DEFAULT_PURPOSE)
    parser.add_argument("--speak-dispatch", action="store_true", help="say a short TTS acknowledgement after dispatch")
    parser.add_argument("--speak-text", default="Saadetud.", help="acknowledgement text for --speak-dispatch")
    parser.add_argument("--tts-url", default=DEFAULT_TTS_URL)
    parser.add_argument("--tts-speaker", default=DEFAULT_TTS_SPEAKER)
    parser.add_argument("--tts-speed", type=float, default=DEFAULT_TTS_SPEED)
    parser.add_argument("--tts-player", help="audio player command, e.g. 'paplay' or 'play -q'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    profiles = subparsers.add_parser("profiles", help="list configured agent profiles")
    profiles.set_defaults(func=list_profiles)

    pane = subparsers.add_parser("pane", help="start a blank tmux target pane")
    pane.add_argument("--session", default="kratt-thesis-agent")
    pane.set_defaults(func=start_blank_pane)

    agent = subparsers.add_parser("agent", help="start an interactive dispatcher agent in tmux")
    agent.add_argument("--session", default="kratt-thesis-agent")
    add_profile_args(agent)
    agent.set_defaults(func=start_agent)

    send = subparsers.add_parser("send", help="dispatch one already-transcribed request")
    send.add_argument("text", nargs="+")
    send.add_argument("--mode", choices=["raw-pane", "tmux-pane", "worker-window"], default="raw-pane")
    send.add_argument("--target", default=DEFAULT_TARGET)
    send.add_argument("--session", default=DEFAULT_WORKER_SESSION)
    add_profile_args(send)
    send.add_argument("--max-budget-usd")
    send.add_argument(
        "--submit-key",
        default=DEFAULT_SUBMIT_KEY,
        help="tmux key sent after input text",
    )
    send.add_argument(
        "--input-method",
        choices=["paste", "type"],
        default=DEFAULT_INPUT_METHOD,
        help="paste-buffer or literal tmux typing; use type for Codex TUI if paste mode will not submit",
    )
    send.add_argument(
        "--submit-delay-ms",
        type=int,
        default=DEFAULT_SUBMIT_DELAY_MS,
        help="delay between text input and the separate tmux submit key",
    )
    send.add_argument("--no-enter", action="store_true")
    send.add_argument("--dry-run", action="store_true")
    add_voice_args(send)
    send.set_defaults(func=lambda args: dispatch_text(args, " ".join(args.text)))

    listen_parser = subparsers.add_parser("listen", help="listen with Kiirkirjutaja and dispatch final transcripts")
    listen_parser.add_argument("--device")
    listen_parser.add_argument("--list-devices", action="store_true")
    listen_parser.add_argument("--image", default="kiirkirjutaja-int8-local")
    listen_parser.add_argument("--no-build", action="store_true")
    listen_parser.add_argument("--show-partial", action="store_true")
    listen_parser.add_argument("--mode", choices=["raw-pane", "tmux-pane", "worker-window"], default="raw-pane")
    listen_parser.add_argument("--target", default=DEFAULT_TARGET)
    listen_parser.add_argument("--session", default=DEFAULT_WORKER_SESSION)
    add_profile_args(listen_parser)
    listen_parser.add_argument("--max-budget-usd")
    listen_parser.add_argument(
        "--submit-key",
        default=DEFAULT_SUBMIT_KEY,
        help="tmux key sent after input text",
    )
    listen_parser.add_argument(
        "--input-method",
        choices=["paste", "type"],
        default=DEFAULT_INPUT_METHOD,
        help="paste-buffer or literal tmux typing; use type for Codex TUI if paste mode will not submit",
    )
    listen_parser.add_argument(
        "--submit-delay-ms",
        type=int,
        default=DEFAULT_SUBMIT_DELAY_MS,
        help="delay between text input and the separate tmux submit key",
    )
    listen_parser.add_argument("--no-enter", action="store_true")
    listen_parser.add_argument("--dry-run", action="store_true")
    add_voice_args(listen_parser)
    listen_parser.set_defaults(func=listen)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
