#!/usr/bin/env python3
"""Fill the written quote/invoice from an intake JSON file.

Bank account fields are left as braced tokens. Fill those privately
when the quote is sent. Do not write the filled bank details back to git.

Keith does not draft this file. CoS runs this script, then sends it.
Keith's manual step is later: confirming the deposit has cleared.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "quote-template.html"
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
REQUIRED = (
    "business_name",
    "email",
    "what_you_do",
    "services",
    "area",
    "tone",
    "home_offer",
    "about_facts",
    "contact_details",
    "fifth_page",
    "fifth_page_notes",
    "domain",
    "hosting",
    "photo_notes",
)
FIFTH = {"gallery": "Gallery", "faq": "FAQ", "pricing": "Pricing"}
HOSTING = {
    "cloudflare-pages": "Your own Cloudflare Pages account (free plan), or a zip if you prefer.",
    "github-pages": "Your own GitHub Pages account (free plan), or a zip if you prefer.",
    "zip": "A zip of the files. You host them yourself.",
}
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
BANK_TOKENS = ("BANK_ACCOUNT_NAME", "BANK_SORT_CODE", "BANK_ACCOUNT_NUMBER")


def uk_date(value: date) -> str:
    return f"{value.day} {MONTHS[value.month - 1]} {value.year}"


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().casefold()
    return text in {"1", "true", "yes", "on", "y"}


def load_intake(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Intake JSON must be an object.")
    if not data.get("contact_name") and data.get("name"):
        data["contact_name"] = data["name"]
    missing = [key for key in REQUIRED if not str(data.get(key, "")).strip()]
    if not str(data.get("contact_name", "")).strip():
        missing.insert(0, "contact_name")
    if missing:
        raise SystemExit("Intake is missing: " + ", ".join(missing))
    fifth = str(data["fifth_page"]).strip().casefold()
    if fifth not in FIFTH:
        raise SystemExit("fifth_page must be gallery, faq or pricing.")
    data["fifth_page"] = fifth
    hosting = str(data["hosting"]).strip().casefold()
    if hosting not in HOSTING:
        raise SystemExit("hosting must be cloudflare-pages, github-pages or zip.")
    data["hosting"] = hosting
    return data


def fill(template: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in values:
            return html.escape(values[key], quote=True)
        return match.group(0)

    return TOKEN.sub(repl, template)


def build(intake: dict, invoice_number: str, invoice_date: date, due: date) -> str:
    early = as_bool(intake.get("early_start"))
    if early:
        early_note = (
            "You ticked the box asking us to start work within the 14-day cancellation period. "
            "If you cancel after work has started, you will pay for the work done up to cancellation."
        )
    else:
        early_note = (
            "You did not ask us to start within the 14-day cancellation period. "
            "The optional box on the form was left unticked. We will not start until that period has ended, "
            "unless you later ask in writing, using these words: "
            "I ask you to start work within the 14-day cancellation period and understand I'll pay for work done if I cancel."
        )
    must_not = str(intake.get("must_not_claim") or "").strip() or "None stated."
    values = {
        "INVOICE_NUMBER": invoice_number,
        "INVOICE_DATE": uk_date(invoice_date),
        "DUE_DATE": uk_date(due),
        "CONTACT_NAME": str(intake["contact_name"]).strip(),
        "BUSINESS_NAME": str(intake["business_name"]).strip(),
        "EMAIL": str(intake["email"]).strip(),
        "FIFTH_PAGE_LABEL": FIFTH[intake["fifth_page"]],
        "WHAT_YOU_DO": str(intake["what_you_do"]).strip(),
        "SERVICES": str(intake["services"]).strip(),
        "AREA": str(intake["area"]).strip(),
        "TONE": str(intake["tone"]).strip(),
        "HOME_OFFER": str(intake["home_offer"]).strip(),
        "ABOUT_FACTS": str(intake["about_facts"]).strip(),
        "CONTACT_DETAILS": str(intake["contact_details"]).strip(),
        "FIFTH_PAGE_NOTES": str(intake["fifth_page_notes"]).strip(),
        "PHOTO_NOTES": str(intake["photo_notes"]).strip(),
        "DOMAIN": str(intake["domain"]).strip(),
        "HOSTING_LABEL": HOSTING[intake["hosting"]],
        "MUST_NOT_CLAIM": must_not,
        "EARLY_START_NOTE": early_note,
    }
    rendered = fill(TEMPLATE.read_text(encoding="utf-8"), values)
    for token in BANK_TOKENS:
        needle = "{{" + token + "}}"
        if needle not in rendered:
            raise SystemExit(f"Bank token {needle} was overwritten. Refusing to write the quote.")
    if "Keith Bullock, trading as NewCo Studio" not in rendered:
        raise SystemExit("Signature line missing.")
    return rendered


def parse_iso(value: str) -> date:
    try:
        year, month, day = (int(part) for part in value.split("-"))
        return date(year, month, day)
    except ValueError as exc:
        raise SystemExit(f"Date must be YYYY-MM-DD, not {value!r}.") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a quote/invoice HTML file from intake JSON.")
    parser.add_argument("intake", type=Path, nargs="?", help="Path to intake JSON")
    parser.add_argument("-o", "--output", type=Path, help="Where to write the HTML. Defaults to stdout.")
    parser.add_argument("--invoice-number", default="", help="Invoice number. Default NCS-299-YYYYMMDD.")
    parser.add_argument("--date", default="", help="Invoice date, YYYY-MM-DD. Default today.")
    parser.add_argument("--due", default="", help="Deposit due date, YYYY-MM-DD. Default seven days on.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checks and exit.")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.intake:
        parser.error("intake JSON is required")
    invoice_date = parse_iso(args.date) if args.date else date.today()
    due = parse_iso(args.due) if args.due else invoice_date + timedelta(days=7)
    number = args.invoice_number.strip() or f"NCS-299-{invoice_date:%Y%m%d}"
    rendered = build(load_intake(args.intake), number, invoice_date, due)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(rendered)
    return 0


def self_test() -> int:
    intake = load_intake(ROOT / "intake.example.json")
    rendered = build(intake, "NCS-299-20261123", date(2026, 11, 23), date(2026, 11, 30))
    checks = [
        "Keith Bullock, trading as NewCo Studio",
        "keith@newcopacks.co.uk",
        "£149.50",
        "£299 fixed",
        "VAT is not charged",
        "NCS-299-20261123",
        "30 November 2026",
        "{{BANK_SORT_CODE}}",
        "{{BANK_ACCOUNT_NAME}}",
        "{{BANK_ACCOUNT_NUMBER}}",
        "14 days",
        "left unticked",
        "North Lane Flowers",
        "One revision round",
    ]
    for needle in checks:
        if needle not in rendered:
            raise SystemExit(f"self-test missing {needle!r}")
    if rendered.count("£149.50") < 3:
        raise SystemExit("self-test expected the deposit and the balance to be stated")
    lowered = rendered.casefold()
    for banned in ("telephone", "phone number", "home address", "trader address", "sort code</dt><dd>12"):
        if banned in lowered:
            raise SystemExit(f"self-test found disallowed text: {banned}")
    early = dict(intake)
    early["early_start"] = "yes"
    ticked = build(early, "NCS-299-20261123", date(2026, 11, 23), date(2026, 11, 30))
    if "You ticked the box" not in ticked or "{{BANK_SORT_CODE}}" not in ticked:
        raise SystemExit("self-test early-start path failed")
    print("generate_quote.py self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
