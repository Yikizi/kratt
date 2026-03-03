#!/usr/bin/env python3
"""Download a Common Voice mirror snapshot from Hugging Face."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Common Voice mirror files from Hugging Face."
    )
    parser.add_argument(
        "--dataset",
        default="malaysia-ai/common_voice_17_0",
        help="Hugging Face dataset id.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Destination directory.",
    )
    parser.add_argument(
        "--include",
        nargs="+",
        default=["README.md", "data/*.parquet", "*.zip"],
        help="Allow patterns passed to snapshot_download.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Parallel workers for the download.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=args.dataset,
        repo_type="dataset",
        allow_patterns=args.include,
        local_dir=str(output_dir),
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    main()
