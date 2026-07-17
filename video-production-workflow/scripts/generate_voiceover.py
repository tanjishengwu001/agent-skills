#!/usr/bin/env python3
"""Generate one voice-over audio file per storyboard shot."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class Shot:
    id: str
    text: str | None


class Provider(Protocol):
    supported_formats: tuple[str, ...]
    def validate(self, config: argparse.Namespace) -> None: ...
    async def synthesize(self, text: str, output_path: Path, config: argparse.Namespace) -> None: ...


class EdgeProvider:
    supported_formats = ("mp3",)

    def validate(self, config: argparse.Namespace) -> None:
        if config.format not in self.supported_formats:
            raise ValueError("edge supports only: mp3")
        try:
            import edge_tts  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("edge-tts is required; install it with: pip install edge-tts") from exc

    async def synthesize(self, text: str, output_path: Path, config: argparse.Namespace) -> None:
        import edge_tts
        await edge_tts.Communicate(text, config.voice, rate=config.rate).save(str(output_path))


PROVIDERS: dict[str, Provider] = {"edge": EdgeProvider()}
DEFAULT_VOICES = {"zh": "zh-CN-XiaoxiaoNeural", "en": "en-US-JennyNeural", "ja": "ja-JP-NanamiNeural"}


def read_storyboard(path: Path) -> list[Shot]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next((i for i, line in enumerate(lines) if line.strip().startswith("|") and "Shot" in line and "Narration" in line), None)
    if header_index is None:
        raise ValueError("Storyboard must contain a Markdown table with Shot and Narration columns.")
    headers = [cell.strip().lower() for cell in lines[header_index].strip().strip("|").split("|")]
    shot_col, narration_col = headers.index("shot"), headers.index("narration")
    shots: list[Shot] = []
    for line in lines[header_index + 2:]:
        if not line.strip().startswith("|"):
            if shots:
                break
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) <= max(shot_col, narration_col):
            continue
        shot_id, text = cells[shot_col], re.sub(r"\s+", " ", cells[narration_col]).strip()
        if shot_id and set(shot_id) != {"-"}:
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", shot_id):
                raise ValueError(f"Invalid shot id: {shot_id!r}. Use letters, digits, _ or - only.")
            shots.append(Shot(shot_id, text))
    if not shots:
        raise ValueError("No shot rows found in storyboard.")
    if len({shot.id for shot in shots}) != len(shots):
        raise ValueError("Shot ids must be unique.")
    return shots


def default_voice(shots: list[Shot]) -> str:
    text = "".join(shot.text or "" for shot in shots)
    if re.search(r"[\u3040-\u30ff]", text):
        return DEFAULT_VOICES["ja"]
    if re.search(r"[\u4e00-\u9fff]", text):
        return DEFAULT_VOICES["zh"]
    return DEFAULT_VOICES["en"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate shot-aligned voice-over audio from a Markdown storyboard.")
    parser.add_argument("--storyboard", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--provider", default="edge", choices=sorted(PROVIDERS))
    parser.add_argument("--voice")
    parser.add_argument("--rate", default="+0%")
    parser.add_argument("--format", default="mp3")
    parser.add_argument("--synthesize", action="store_true", help="Perform synthesis; otherwise only write the manifest.")
    args = parser.parse_args()
    try:
        shots = read_storyboard(args.storyboard)
        args.voice = args.voice or default_voice(shots)
        provider = PROVIDERS[args.provider]
        args.output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        if args.synthesize:
            provider.validate(args)
            for shot in shots:
                if not shot.text:
                    results.append({"id": shot.id, "text": "", "file": None, "status": "skipped"})
                    continue
                output = args.output_dir / f"{shot.id}.{args.format}"
                try:
                    asyncio.run(provider.synthesize(shot.text, output, args))
                    results.append({"id": shot.id, "text": shot.text, "file": output.name, "status": "success"})
                except Exception as exc:  # Keep the remaining shots independently usable.
                    results.append({"id": shot.id, "text": shot.text, "file": None, "status": "failed", "error": str(exc)})
        else:
            results = [
                {"id": shot.id, "text": shot.text or "", "file": f"{shot.id}.{args.format}" if shot.text else None, "status": "pending" if shot.text else "skipped"}
                for shot in shots
            ]
        manifest = {"version": 1, "provider": args.provider, "voice": args.voice, "rate": args.rate, "format": args.format, "shots": results}
        manifest_path = args.output_dir / "voiceover-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        counts = {status: sum(item["status"] == status for item in results) for status in ("success", "pending", "skipped", "failed")}
        print(f"Wrote {manifest_path} ({len(shots)} shots; {counts['success']} success, {counts['pending']} pending, {counts['skipped']} skipped, {counts['failed']} failed)")
        return 1 if counts["failed"] else 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
