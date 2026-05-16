# Thesis voice dispatch

Purpose: let Mattias read the thesis, dictate a small correction, and route the
transcribed request into a terminal agent without turning the voice loop into the
worker.

The same Kiirkirjutaja/TTS plumbing is also available for general repo work as
`kratt dev-voice`; it uses coding-focused prompts instead of thesis-editing
prompts. For the Android on-device dictation MVP and lessons learned, see
`docs/automation/android-dev-voice-session-lessons-2026-05-08.md`.

This is intentionally narrow thesis-deadline tooling. It does not replace the
existing `.hermes/thesis-automation/` lane system; it is for ad-hoc corrections
noticed while reading the PDF.

## Flow

```
Mattias reads PDF
  -> says one correction request
  -> Kiirkirjutaja INT8 emits a final transcript
  -> kratt thesis-voice sends it through tmux with Enter
  -> whichever agent is in that pane handles it
```

## Simple tmux target

Default mode is intentionally simple: create an empty tmux pane, start whatever
agent you want inside it, and let the transcription loop paste final transcripts
with Enter.

```bash
kratt thesis-voice pane
tmux attach -t kratt-thesis-agent
```

Inside that tmux pane, start the agent manually, for example `c`, Claude Code,
Codex YOLO, or a Pi-agent shell. Then dispatch typed text:

```bash
kratt thesis-voice send "siin lehel 3 on sanity check"
```

Live microphone mode uses the same raw-pane default:

```bash
kratt thesis-voice listen --device 1
```

If the target pane is Codex and submitted text turns into a new line instead of
being sent, avoid tmux paste mode and send literal key input:

```bash
kratt thesis-voice listen --device 1 --input-method type --submit-delay-ms 150
kratt thesis-voice send --input-method type --submit-delay-ms 150 "siin lehel 3 on sanity check"
```

You can also make that persistent for the shell:

```bash
export KRATT_THESIS_VOICE_INPUT_METHOD=type
export KRATT_THESIS_VOICE_SUBMIT_DELAY_MS=150
```

If Codex still inserts a newline, bind Codex composer submit to a key tmux can
send, then use that key from `thesis-voice`. For example in `~/.codex/config.toml`:

```toml
[tui.keymap.composer]
submit = "ctrl-g"
```

Then run:

```bash
kratt thesis-voice listen --device 1 --input-method type --submit-key C-g
```

Say `stop` or `stopp` as a standalone utterance to send `Escape` to the target
pane instead of submitting text. This is useful for interrupting the agent while
keeping the transcription loop running.

## PDF page guardrail

When a dictated request mentions a PDF page, agents must use the canonical thesis
PDF `docs/thesis/thesis-tex-estonian/main.pdf`. Stale sibling PDFs such as
`loputoo.pdf` are ignored unless the request explicitly names that file. If page
layout matters, rebuild or check freshness before trusting a page number.

For deliberate per-page critique batches, prefer:

```bash
kratt thesis-page-critique --build --pages 1-70
```

This creates prompts with a PDF SHA-256, page count, extracted page text, and a
forbidden-sibling-PDF list so future review runs do not drift across PDFs.

## Wrapped dispatcher mode

The older wrapped mode is still available when you want every transcript to be
expanded into a scoped thesis-correction prompt before it is pasted into the
agent:

```bash
kratt thesis-voice agent
tmux attach -t kratt-thesis-agent
kratt thesis-voice send --mode tmux-pane "siin lehel 3 on sanity check"
```

For Claude Code this can launch with `--dangerously-skip-permissions`. The
initial prompt tells the dispatcher to put concrete edits into background
agents/workers automatically and keep the parent session free for more dictated
requests.

## Agent profiles

Profiles only affect `agent` and `--mode worker-window`. Simple `pane` mode does
not care what model is used because you start the agent yourself.

Built-in profiles:

```bash
kratt thesis-voice profiles
```

Local config is optional and ignored by git:

```bash
cp cli/tools/thesis_voice_dispatch.config.example.json \
  cli/tools/thesis_voice_dispatch.config.json
```

Example profile usage:

```bash
kratt thesis-voice agent --profile claude-yolo --model sonnet
kratt thesis-voice agent --profile codex-yolo --model gpt-5.3-codex-spark
kratt thesis-voice listen --device 1 --mode worker-window --profile codex-yolo
```

For a Pi agent, edit the `pi-agent` shell profile in local `config.json` with the
real `ssh ...` or local Pi-agent command. Shell profiles support these template
variables: `{{repo}}`, `{{prompt}}`, `{{prompt_q}}`, `{{prompt_path}}`,
`{{prompt_path_q}}`, `{{model}}`, `{{model_q}}`, and `{{max_budget_usd}}`.
The same local config can override control words, for example
`"control_words": {"escape": ["stop", "stopp", "katkesta"]}`.

## Development voice mode

For coding by voice, use the development wrapper:

```bash
kratt dev-voice pane
tmux attach -t kratt-thesis-agent
# start your coding agent in that pane, then in another terminal:
kratt dev-voice listen --device 1 --input-method type --submit-delay-ms 150
```

Optional short spoken acknowledgement via the local TTS server:

```bash
kratt tts-server              # separate terminal, requires tools/text-to-speech-worker models
kratt dev-voice listen --device 1 --speak-dispatch
```

The external runtime sources are expected at:

- `stt-integration/kiirkirjutaja-source/` (git submodule)
- `tools/text-to-speech-worker/` (ignored local clone of TartuNLP worker + submodules)

Fresh checkout bootstrap:

```bash
git submodule update --init --recursive stt-integration/kiirkirjutaja-source
git clone --recurse-submodules https://github.com/TartuNLP/text-to-speech-worker.git \
  tools/text-to-speech-worker
```

## Live microphone mode

List AVFoundation devices:

```bash
kratt thesis-voice listen --list-devices
```

This reuses the trimmed Kiirkirjutaja INT8 Docker runtime under
`stt-integration/kiirkirjutaja-source/`. Final endpoint transcripts are sent to a
tmux pane with Enter.

## Direct worker mode

If the parent dispatcher should stay completely idle, skip the interactive pane
and create one worker tmux window per request:

```bash
kratt thesis-voice send --mode worker-window \
  "lehel 3 on sanity check, paranda see korrektseks eesti keeleks"

kratt thesis-voice listen --device 1 --mode worker-window
```

Workers default to Claude Code in `kratt-thesis-voice-workers`. They are scoped
to one correction, run with `--dangerously-skip-permissions`, and inherit the
repo guardrails in `AGENTS.md` / `CLAUDE.md`.
Use direct worker mode for small, independent fixes; use the dispatcher pane when
the request needs judgment about sequencing or conflicts with a dirty worktree.

## Current limitation

This MVP is not wake-word gated yet. `listen` is continuous dictation: it sends a
prompt whenever the Kiirkirjutaja online recognizer emits a final endpoint
transcript. In a quiet solo-reading workflow this is useful; around other speech
it can dispatch accidental requests. A wake-word gate and audible activation ding
should be the next layer before using it in a shared room.

## Dry run

```bash
kratt thesis-voice send --dry-run "lehel 3 on sanity check"
kratt thesis-voice send --mode tmux-pane --dry-run "lehel 3 on sanity check"
kratt thesis-voice send --mode worker-window --dry-run "lehel 3 on sanity check"
```

Dry run prints the prompt that would be sent.
