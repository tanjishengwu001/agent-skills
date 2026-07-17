#!/usr/bin/env python3
"""Render a 30fps storyboard video whose shot durations equal audio durations."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
FPS = 30
FRAME_TOLERANCE_SECONDS = 1 / FPS


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(
            completed.stderr.strip() or "Command failed: " + " ".join(command)
        )


def audio_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"Could not inspect {path}")
    duration = float(completed.stdout.strip())
    if duration <= 0:
        raise ValueError(f"Audio has non-positive duration: {path}")
    return duration


def probe_final_video(path: Path) -> dict[str, object]:
    """Inspect the final container and return normalized stream metadata."""
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"Could not inspect {path}")
    data = json.loads(completed.stdout)
    streams = data.get("streams", [])
    if not isinstance(streams, list):
        raise ValueError("ffprobe returned invalid stream data.")
    video_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "video"), None
    )
    audio_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"), None
    )
    duration = float(data.get("format", {}).get("duration", 0))
    return {
        "duration_seconds": duration,
        "has_video": video_stream is not None,
        "has_audio": audio_stream is not None,
        "width": int(video_stream.get("width", 0)) if video_stream else 0,
        "height": int(video_stream.get("height", 0)) if video_stream else 0,
        "frame_rate": str(video_stream.get("r_frame_rate", "0/0"))
        if video_stream
        else "0/0",
    }


def frame_rate_value(value: str) -> float:
    try:
        numerator, denominator = (float(part) for part in value.split("/", 1))
        return numerator / denominator if denominator else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


def final_qc(
    path: Path,
    expected_duration: float,
    width: int,
    height: int,
) -> dict[str, object]:
    """Verify the final MP4 against the documented delivery contract."""
    probe = probe_final_video(path)
    duration = float(probe["duration_seconds"])
    drift = abs(duration - expected_duration)
    checks = {
        "has_video": bool(probe["has_video"]),
        "has_audio": bool(probe["has_audio"]),
        "fps_30": abs(frame_rate_value(str(probe["frame_rate"])) - FPS) < 0.001,
        "size_matches": probe["width"] == width and probe["height"] == height,
        "duration_within_one_frame": drift <= FRAME_TOLERANCE_SECONDS,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "expected_duration_seconds": expected_duration,
        "actual_duration_seconds": duration,
        "duration_drift_seconds": drift,
        "tolerance_seconds": FRAME_TOLERANCE_SECONDS,
        "actual_size": f"{probe['width']}x{probe['height']}",
        "actual_frame_rate": probe["frame_rate"],
        "auto_fix_attempted": False,
        "auto_fixed": False,
    }


def reencode_for_qc(
    source: Path,
    destination: Path,
    width: int,
    height: int,
    expected_duration: float,
) -> None:
    """Normalize the final container once when its first QC pass fails."""
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-t",
            str(expected_duration),
            "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(destination),
        ]
    )


def find_image(image_dir: Path, shot_id: str) -> Path | None:
    return next(
        (
            image_dir / f"{shot_id}{extension}"
            for extension in IMAGE_EXTENSIONS
            if (image_dir / f"{shot_id}{extension}").is_file()
        ),
        None,
    )


def probe_image_size(path: Path) -> tuple[int, int]:
    """Detect actual width x height of an image file via ffprobe."""
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            completed.stderr.strip() or f"Could not probe image size: {path}"
        )
    w, h = (int(part) for part in completed.stdout.strip().split("x", 1))
    if w <= 0 or h <= 0:
        raise ValueError(f"Image has invalid dimensions {w}x{h}: {path}")
    return w, h


def detect_size_from_images(image_dir: Path, shot_ids: list[str]) -> tuple[int, int]:
    """Auto-detect output size from the first available image."""
    for shot_id in shot_ids:
        img = find_image(image_dir, shot_id)
        if img is not None:
            w, h = probe_image_size(img)
            # Ensure even dimensions for H.264 compatibility
            if w % 2:
                w += 1
            if h % 2:
                h += 1
            return w, h
    raise RuntimeError(
        "No images found to auto-detect size; specify --size explicitly."
    )


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "size must be WIDTHxHEIGHT, for example 1920x1080"
        ) from exc
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise argparse.ArgumentTypeError(
            "width and height must be positive even integers"
        )
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a shot-aligned 30fps MP4 from images and voice-over audio."
    )
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--image-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--size",
        type=parse_size,
        default=None,
        help="Output resolution WIDTHxHEIGHT. If omitted, auto-detected from the first image.",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render MP4; otherwise only validate inputs and write a manifest.",
    )
    args = parser.parse_args()
    manifest_path = args.audio_dir / "voiceover-manifest.json"
    try:
        voiceover = json.loads(manifest_path.read_text(encoding="utf-8"))
        if voiceover.get("version") != 1 or not isinstance(
            voiceover.get("shots"), list
        ):
            raise ValueError("Invalid voiceover manifest schema.")
        if args.render and (not shutil.which("ffmpeg") or not shutil.which("ffprobe")):
            raise RuntimeError("ffmpeg and ffprobe are required to render video.")
        # Auto-detect output size from actual images if --size not specified
        if args.size is not None:
            width, height = args.size
        else:
            shot_ids = [str(s.get("id", "")) for s in voiceover["shots"]]
            width, height = detect_size_from_images(args.image_dir, shot_ids)
            print(f"Auto-detected image size: {width}x{height}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        segments_dir = args.output.parent / ".segments"
        results: list[dict[str, object]] = []
        cumulative_audio_seconds = 0.0
        allocated_frames = 0
        for shot in voiceover["shots"]:
            shot_id, audio_file, status = (
                str(shot.get("id", "")),
                shot.get("file"),
                shot.get("status"),
            )
            if status == "skipped":
                results.append({"id": shot_id, "status": "skipped"})
                continue
            if status not in {"success", "pending"} or not isinstance(audio_file, str):
                results.append(
                    {
                        "id": shot_id,
                        "status": "failed",
                        "error": "Audio is not renderable in voiceover manifest.",
                    }
                )
                continue
            audio = args.audio_dir / audio_file
            image = find_image(args.image_dir, shot_id)
            if not audio.is_file() or image is None:
                missing = "audio" if not audio.is_file() else "image"
                results.append(
                    {"id": shot_id, "status": "failed", "error": f"Missing {missing}."}
                )
                continue
            try:
                duration = audio_duration(audio) if args.render else None
            except (RuntimeError, ValueError) as exc:
                results.append({"id": shot_id, "status": "failed", "error": str(exc)})
                continue
            segment = segments_dir / f"{shot_id}.mp4"
            result = {
                "id": shot_id,
                "image": str(image),
                "audio": str(audio),
                "segment": str(segment),
                "status": "pending",
            }
            if duration is not None:
                cumulative_audio_seconds += duration
                target_frames = (
                    int(cumulative_audio_seconds * FPS + 0.5) - allocated_frames
                )
                target_frames = max(target_frames, 1)
                allocated_frames += target_frames
                result["audio_duration_seconds"] = duration
                result["video_frames"] = target_frames
                result["video_duration_seconds"] = target_frames / FPS
            results.append(result)
        failed = [item for item in results if item["status"] == "failed"]
        renderable = [item for item in results if item["status"] == "pending"]
        if args.render and not failed and renderable:
            segments_dir.mkdir(parents=True, exist_ok=True)
            video_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
            for item in renderable:
                try:
                    run(
                        [
                            "ffmpeg",
                            "-y",
                            "-loop",
                            "1",
                            "-framerate",
                            str(FPS),
                            "-i",
                            str(item["image"]),
                            "-i",
                            str(item["audio"]),
                            "-t",
                            str(item["video_duration_seconds"]),
                            "-map",
                            "0:v:0",
                            "-map",
                            "1:a:0",
                            "-vf",
                            video_filter,
                            "-af",
                            f"apad=whole_dur={item['video_duration_seconds']}",
                            "-r",
                            str(FPS),
                            "-c:v",
                            "libx264",
                            "-crf",
                            "18",
                            "-preset",
                            "medium",
                            "-c:a",
                            "aac",
                            "-b:a",
                            "192k",
                            "-movflags",
                            "+faststart",
                            str(item["segment"]),
                        ]
                    )
                    item["status"] = "success"
                except RuntimeError as exc:
                    item["status"] = "failed"
                    item["error"] = str(exc)
            failed = [item for item in results if item["status"] == "failed"]
            if not failed:
                concat_file = args.output.parent / ".concat.txt"
                concat_file.write_text(
                    "".join(
                        f"file '{Path(str(item['segment'])).resolve()}'\n"
                        for item in renderable
                    ),
                    encoding="utf-8",
                )
                run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(concat_file),
                        "-c",
                        "copy",
                        "-movflags",
                        "+faststart",
                        str(args.output),
                    ]
                )
        qc: dict[str, object] = {"ok": None, "status": "not-run"}
        if args.render and renderable and not failed:
            qc = final_qc(
                args.output,
                cumulative_audio_seconds,
                width,
                height,
            )
            if not qc["ok"]:
                qc["auto_fix_attempted"] = True
                fixed_output = args.output.with_name(
                    f"{args.output.stem}.qc-fixed{args.output.suffix}"
                )
                try:
                    reencode_for_qc(
                        args.output,
                        fixed_output,
                        width,
                        height,
                        cumulative_audio_seconds,
                    )
                    fixed_output.replace(args.output)
                    qc = final_qc(
                        args.output,
                        cumulative_audio_seconds,
                        width,
                        height,
                    )
                    qc["auto_fix_attempted"] = True
                    qc["auto_fixed"] = bool(qc["ok"])
                except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
                    qc["auto_fix_error"] = str(exc)
                    if fixed_output.exists():
                        fixed_output.unlink()
        status = (
            "failed"
            if failed
            else "dry-run"
            if not args.render
            else "success"
            if renderable and qc.get("ok") is True
            else "failed"
        )
        output_manifest = {
            "version": 1,
            "fps": FPS,
            "size": f"{width}x{height}",
            "output": str(args.output),
            "status": status,
            "shots": results,
            "final_qc": qc,
        }
        output_manifest_path = args.output.parent / "video-manifest.json"
        output_manifest_path.write_text(
            json.dumps(output_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"Wrote {output_manifest_path} ({len(renderable)} renderable, {len(failed)} failed; {'rendered' if args.render else 'dry run'})"
        )
        return 1 if status == "failed" else 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
