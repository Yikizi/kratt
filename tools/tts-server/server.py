#!/usr/bin/env python3
"""Lightweight HTTP wrapper around TartuNLP TTS worker.

Loads the multispeaker Synthesizer once and serves a simple POST API.

Usage:
    python server.py                          # default port 5380
    python server.py --port 5381

API:
    POST /synthesize
    Body: {"text": "Tere!", "speaker": "meelis", "speed": 1.0}
    Response: WAV audio (audio/wav)

    GET /speakers
    Response: {"speakers": ["albert", "indrek", ...]}
"""
from __future__ import annotations

import argparse
import io
import logging
import os
import sys
import time
from pathlib import Path

# Suppress TF warnings before importing anything else
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

import uvicorn

# Add TTS worker to path
TTS_WORKER_DIR = Path(__file__).resolve().parent.parent / "text-to-speech-worker"
sys.path.insert(0, str(TTS_WORKER_DIR))

from tts_worker.config import read_model_config
from tts_worker.synthesizer import Synthesizer
from tts_worker.schemas import Request as TTSRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Kratt TTS Server")

synth: Synthesizer | None = None
speaker_list: list[str] = []


class SynthRequest(BaseModel):
    text: str
    speaker: str = "meelis"
    speed: float = 1.0


@app.on_event("startup")
def load_model():
    global synth, speaker_list
    config_path = str(TTS_WORKER_DIR / "config" / "config.yaml")
    model_config = read_model_config(config_path, "multispeaker")
    # Resolve model_path relative to TTS worker dir
    model_config.model_path = str(TTS_WORKER_DIR / model_config.model_path)
    logger.info(f"Loading TTS model from {model_config.model_path}...")
    t0 = time.time()
    synth = Synthesizer(model_config)
    speaker_list = sorted(model_config.speakers.keys())
    logger.info(f"TTS ready in {time.time() - t0:.1f}s — speakers: {speaker_list}")


@app.get("/speakers")
def get_speakers():
    return {"speakers": speaker_list}


@app.post("/synthesize")
def synthesize(req: SynthRequest):
    if synth is None:
        raise HTTPException(503, "TTS model not loaded")
    if req.speaker not in speaker_list:
        raise HTTPException(400, f"Unknown speaker '{req.speaker}'. Available: {speaker_list}")
    if not req.text.strip():
        raise HTTPException(400, "Empty text")

    t0 = time.time()
    tts_req = TTSRequest(text=req.text, speaker=req.speaker, speed=req.speed)
    result = synth.process_request(tts_req)
    elapsed = time.time() - t0
    logger.info(f"Synthesized '{req.text[:50]}...' ({req.speaker}) in {elapsed:.2f}s")

    return Response(content=result.content.audio, media_type="audio/wav")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5380)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
