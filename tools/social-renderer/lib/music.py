"""Music metadata gates. No soundtrack is invented or claimed licensed without user meta."""

from __future__ import annotations

from pathlib import Path
from typing import Any


REQUIRED_META_KEYS = (
    "title",
    "artist_or_uploader",
    "source_url",
    "licence",
    "licence_url",
    "cross_platform_ok",
    "file",
)


def validate_music(cfg: dict[str, Any], root: Path, *, for_video: bool) -> list[str]:
    """Return list of error strings. Empty = ok for the requested mode."""
    errors: list[str] = []
    music = cfg.get("music")

    if not for_video:
        # Preview / contact-sheet path: music optional, but if present must be coherent.
        if music is None:
            return errors
        return _validate_block(music, root, allow_test_only=True)

    if music is None:
        errors.append(
            "video requires music: supply a cross-platform licensed track + music metadata, "
            "or set music.test_only=true with fixtures/test_only_audio (not publication-ready)."
        )
        return errors

    return _validate_block(music, root, allow_test_only=True)


def _validate_block(music: dict[str, Any], root: Path, *, allow_test_only: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(music, dict):
        return ["music must be an object with licence metadata"]

    test_only = bool(music.get("test_only"))
    if test_only and not allow_test_only:
        errors.append("test_only music cannot be used for publication-ready video")

    for key in REQUIRED_META_KEYS:
        if key not in music or music[key] in (None, ""):
            errors.append(f"music.{key} is required")

    if music.get("cross_platform_ok") is not True and not test_only:
        errors.append(
            "music.cross_platform_ok must be true for real tracks "
            "(do not use platform-only library music)"
        )

    if test_only:
        title = str(music.get("title") or "")
        if "TEST ONLY" not in title.upper():
            errors.append("test_only music.title must include 'TEST ONLY'")
        lic = str(music.get("licence") or "")
        if "TEST ONLY" not in lic.upper() and "NOT FOR PUBLICATION" not in lic.upper():
            errors.append(
                "test_only music.licence must say TEST ONLY or NOT FOR PUBLICATION"
            )

    # Reject false licence claims when using the fixture
    path_raw = music.get("file")
    if path_raw:
        path = (root / path_raw).resolve() if not Path(path_raw).is_absolute() else Path(path_raw)
        try:
            path.relative_to(root.resolve())
        except ValueError:
            # absolute under root also ok if resolve stays inside; else reject later
            pass
        if not path.is_file():
            errors.append(f"music.file not found: {path_raw}")
        else:
            name = path.name.upper()
            if test_only and "TEST_ONLY" not in name and "TEST ONLY" not in name:
                errors.append("test_only audio filename must contain TEST_ONLY")
            if (not test_only) and "TEST_ONLY" in name:
                errors.append("publication music cannot use a TEST_ONLY fixture file")

    if music.get("platform_only") is True:
        errors.append("platform_only tracks are rejected; supply a cross-platform licence")

    return errors


def resolve_audio_path(cfg: dict[str, Any], root: Path) -> Path | None:
    music = cfg.get("music")
    if not music or not music.get("file"):
        return None
    raw = music["file"]
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    return path.resolve()
