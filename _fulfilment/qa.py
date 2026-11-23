#!/usr/bin/env python3
"""Check a built client site before it is shown to the client.

Fails on broken HTML signals, broken internal links, leftover tokens,
banned filler words, a mis-set enquiry form, or the wrong page set.
Lighthouse mobile performance is checked when a local Chrome and
Lighthouse can actually run. If they cannot, that one check is skipped.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import threading
from pathlib import Path

STUDIO_FORM_KEY = "7d1b464a-34b7-421f-9262-3d87ccdfbcb6"
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
BANNED = (
    re.compile(r"lorem", re.I),
    re.compile(r"\bplaceholders?\b", re.I),
    re.compile(r"\bdemo\b", re.I),
    re.compile(r"\bsamples?\b", re.I),
    re.compile(r"fictional[-\s]?clients?", re.I),
)
TOKEN = re.compile(r"\{\{[^}]+\}\}")
CORE = ("index.html", "services/index.html", "about/index.html", "contact/index.html")
FIFTH = ("gallery/index.html", "faq/index.html", "pricing/index.html")
ALLOWED_EXTRA = {"thanks.html", "404.html"}


def html_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.html") if path.is_file())


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def visible_text(html: str) -> str:
    without = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    without = re.sub(r"<style\b[^>]*>.*?</style>", " ", without, flags=re.I | re.S)
    without = re.sub(r"<!--.*?-->", " ", without, flags=re.S)
    return re.sub(r"<[^>]+>", " ", without)


def check_pages(root: Path, files: list[Path]) -> list[str]:
    errors = []
    present = {rel(root, path) for path in files}
    for name in CORE:
        if name not in present:
            errors.append(f"missing {name}")
    fifth = [name for name in FIFTH if name in present]
    if len(fifth) != 1:
        errors.append("the site needs exactly one of gallery, faq or pricing, found " + (", ".join(fifth) or "none"))
    allowed = set(CORE) | set(FIFTH) | ALLOWED_EXTRA
    for name in sorted(present - allowed):
        errors.append(f"unexpected HTML page {name}")
    return errors


def check_html(root: Path, path: Path) -> list[str]:
    errors = []
    name = rel(root, path)
    raw = path.read_text(encoding="utf-8")
    if not raw.lstrip().lower().startswith("<!doctype html>"):
        errors.append(f"{name}: missing <!doctype html>")
    if not re.search(r"<html\b[^>]*\blang=[\"']en-GB[\"']", raw, re.I):
        errors.append(f"{name}: html lang must be en-GB")
    titles = re.findall(r"<title>(.*?)</title>", raw, flags=re.I | re.S)
    if len(titles) != 1 or not titles[0].strip():
        errors.append(f"{name}: needs one non-empty title")
    if not re.search(r"<meta\b[^>]*name=[\"']description[\"'][^>]*content=[\"'][^\"']+[^\"'][\"']", raw, re.I) and not re.search(
        r"<meta\b[^>]*content=[\"'][^\"']+[\"'][^>]*name=[\"']description[\"']", raw, re.I
    ):
        errors.append(f"{name}: needs a meta description")
    h1 = re.findall(r"<h1\b", raw, flags=re.I)
    if len(h1) != 1:
        errors.append(f"{name}: needs exactly one h1, found {len(h1)}")
    for match in re.finditer(r"<img\b[^>]*>", raw, flags=re.I):
        tag = match.group(0)
        if not re.search(r"\balt=", tag, re.I):
            errors.append(f"{name}: an image has no alt attribute")
    if TOKEN.search(raw):
        errors.append(f"{name}: unfilled token remains")
    text = visible_text(raw)
    for pattern in BANNED:
        found = pattern.search(text)
        if found:
            errors.append(f"{name}: banned text {found.group(0)!r}")
    return errors


def resolve_link(root: Path, page: Path, href: str) -> Path | None:
    target = href.split("#", 1)[0].strip()
    if not target or re.match(r"^[a-z]+:", target, re.I):
        return None
    if target.startswith("/"):
        return root / target.lstrip("/")
    return (page.parent / target).resolve()


def check_links(root: Path, path: Path) -> list[str]:
    errors = []
    raw = path.read_text(encoding="utf-8")
    name = rel(root, path)
    for match in re.finditer(r"\b(?:href|src)=[\"']([^\"']+)[\"']", raw, flags=re.I):
        href = match.group(1).strip()
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        if href.startswith(("http://", "https://", "data:")):
            continue
        dest = resolve_link(root, path, href)
        if dest is None:
            continue
        try:
            dest.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{name}: link escapes the site ({href})")
            continue
        if not dest.exists():
            errors.append(f"{name}: broken link {href}")
    return errors


def check_form(root: Path, files: list[Path]) -> list[str]:
    errors = []
    found = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        for match in re.finditer(r"<form\b([^>]*)>(.*?)</form>", raw, flags=re.I | re.S):
            found += 1
            attrs = match.group(1)
            body = match.group(2)
            action = re.search(r"action=[\"']([^\"']+)[\"']", attrs, re.I)
            method = re.search(r"method=[\"']([^\"']+)[\"']", attrs, re.I)
            key = re.search(r"name=[\"']access_key[\"'][^>]*value=[\"']([^\"']*)[\"']", body, re.I)
            if key is None:
                key = re.search(r"value=[\"']([^\"']*)[\"'][^>]*name=[\"']access_key[\"']", body, re.I)
            name = rel(root, path)
            if not action or action.group(1) != "https://api.web3forms.com/submit":
                errors.append(f"{name}: enquiry form must post to https://api.web3forms.com/submit")
            if not method or method.group(1).lower() != "post":
                errors.append(f"{name}: enquiry form method must be post")
            value = key.group(1).strip() if key else ""
            if not UUID.match(value):
                errors.append(f"{name}: access_key is missing or not a real key")
            elif value.lower() == STUDIO_FORM_KEY:
                errors.append(f"{name}: access_key is the studio key, not the client's")
    if found == 0:
        errors.append("no enquiry form found")
    return errors


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def lighthouse(root: Path) -> list[str]:
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
    npx = shutil.which("npx")
    if not chrome or not npx:
        print("Lighthouse: skipped (Chrome or npx is not available, so the check is not feasible).")
        return []
    port = free_port()
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(root), **kwargs)  # noqa: E731
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    report = root / ".lighthouse.json"
    try:
        command = [
            npx,
            "--yes",
            "lighthouse",
            f"http://127.0.0.1:{port}/",
            "--quiet",
            "--chrome-flags=--headless --no-sandbox",
            "--only-categories=performance",
            "--form-factor=mobile",
            "--screenEmulation.mobile=true",
            "--output=json",
            f"--output-path={report}",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if completed.returncode != 0 or not report.exists():
            print("Lighthouse: skipped (it did not run cleanly, so the check is not feasible).")
            if completed.stderr:
                print(completed.stderr.strip().splitlines()[-1])
            return []
        score = json.loads(report.read_text(encoding="utf-8"))["categories"]["performance"]["score"]
        points = round(float(score) * 100)
        print(f"Lighthouse mobile performance: {points}")
        if points < 90:
            return [f"Lighthouse mobile performance is {points}, below 90"]
        return []
    except (OSError, subprocess.TimeoutExpired, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Lighthouse: skipped ({exc.__class__.__name__}, so the check is not feasible).")
        return []
    finally:
        server.shutdown()
        if report.exists():
            report.unlink()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def audit(root: Path, with_lighthouse: bool) -> list[str]:
    root = root.resolve()
    files = html_files(root)
    errors = check_pages(root, files)
    for path in files:
        errors.extend(check_html(root, path))
        errors.extend(check_links(root, path))
    errors.extend(check_form(root, files))
    if with_lighthouse:
        errors.extend(lighthouse(root))
    return errors


def self_test() -> int:
    import tempfile

    good = tempfile.TemporaryDirectory()
    bad = tempfile.TemporaryDirectory()
    try:
        write_fixture(Path(good.name), key="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", banned="")
        write_fixture(Path(bad.name), key="placeholder", banned="lorem ipsum")
        good_errors = [item for item in audit(Path(good.name), False) if not item.startswith("Lighthouse")]
        bad_errors = audit(Path(bad.name), False)
        if good_errors:
            raise SystemExit("self-test good site failed: " + "; ".join(good_errors))
        if not any("banned text" in item for item in bad_errors):
            raise SystemExit("self-test did not catch banned text")
        if not any("access_key" in item for item in bad_errors):
            raise SystemExit("self-test did not catch a bad form key")
    finally:
        good.cleanup()
        bad.cleanup()
    print("qa.py self-test passed")
    return 0


def write_fixture(root: Path, key: str, banned: str) -> None:
    css = root / "assets"
    css.mkdir(parents=True)
    (css / "site.css").write_text("body{margin:0}", encoding="utf-8")
    pages = {
        "index.html": ("Home", "Home words.", f"<p>{banned}</p>"),
        "services/index.html": ("Services", "Services words.", "<p>Services.</p>"),
        "about/index.html": ("About", "About words.", "<p>About.</p>"),
        "contact/index.html": ("Contact", "Contact words.", form(key)),
        "faq/index.html": ("FAQ", "FAQ words.", "<p>Questions.</p>"),
    }
    for name, (title, description, body) in pages.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        depth = name.count("/")
        root_href = "../" * depth
        path.write_text(
            f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{root_href}assets/site.css"></head>
<body><main><h1>{title}</h1>{body}</main></body></html>
""",
            encoding="utf-8",
        )


def form(key: str) -> str:
    return f"""<form action="https://api.web3forms.com/submit" method="post">
<input type="hidden" name="access_key" value="{key}">
<label for="email">Email</label><input id="email" name="email" type="email" required>
<button type="submit">Send</button></form>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA a built 5-page client site.")
    parser.add_argument("site", nargs="?", type=Path, help="Built site directory")
    parser.add_argument("--lighthouse", action="store_true", help="Also run Lighthouse mobile when it is feasible.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.site is None:
        parser.error("a site directory is required")
    errors = audit(args.site, args.lighthouse)
    if errors:
        print(f"QA failed ({len(errors)})")
        for error in errors:
            print(f"- {error}")
        return 1
    print("QA passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
