"""Ticket-delivery rescue on Gametime's public help sentences.

Orders are invented. Sentences are copied from indexed help articles.
A reply may contain only those sentences. Edit rules.json and re-run.

  python delivery.py
"""

from __future__ import annotations

import json
from pathlib import Path

RULES_PATH = Path(__file__).with_name("rules.json")

# Indexed help text, not a live browser render. Sources listed in SOURCES.
SENTENCES = {
    "hold": (
        "For security purposes, many venues will hold the barcodes of their "
        "tickets for 24-48 hours prior to the event."
    ),
    "guarantee": (
        "As an added assurance, we guarantee your tickets will get delivered "
        "before the start of the event."
    ),
    "remedy": (
        "If they aren't, we will look for comparable replacements, or issue "
        "a 110% Gametime credit or full refund if comparable replacements "
        "aren't available."
    ),
    "final": (
        "We do not offer refunds for valid tickets delivered within our "
        "expected timeframe."
    ),
    "resale_block": (
        "If your event is 6 hours or less from the start time, you will not "
        "be able to relist your tickets through our platform."
    ),
    "resale_ok": (
        "If you purchased your tickets through the Gametime platform, you can "
        "list them for sale any time as long as the event is at least 6 hours away."
    ),
    "axs": (
        "This is a notification email and your tickets will drop directly "
        "into your AXS app under tickets."
    ),
    "tm": (
        "If your tickets are sent through Ticketmaster, you will receive a "
        "transfer email to the email address entered at check-out to accept "
        "your tickets."
    ),
}

SOURCES = {
    "hold": "https://support.gametime.co/en_us/ticket-delivery-timeframe-BksQaxsnq",
    "guarantee": "https://support.gametime.co/en_us/ticket-delivery-timeframe-BksQaxsnq",
    "remedy": "https://support.gametime.co/en_us/ticket-delivery-timeframe-BksQaxsnq",
    "final": "https://support.gametime.co/en_us/ticket-delivery-timeframe-BksQaxsnq",
    "resale_block": "https://support.gametime.co/en_us/ticket-resale-availability-ryqjJTT3c",
    "resale_ok": "https://support.gametime.co/en_us/ticket-resale-availability-ryqjJTT3c",
    "axs": "https://support.gametime.co/en_us/ticket-delivery-via-other-platforms-information-ByN2ZEV6q",
    "tm": "https://support.gametime.co/en_us/ticket-delivery-via-other-platforms-information-ByN2ZEV6q",
}

# hours, delivered, channel, request, fan's extra demand that must never ship
CASES = [
    ("D1", 36, False, "gametime", "where", None),
    ("D2", 1, False, "gametime", "where", None),
    ("D3", 4, False, "gametime", "where", None),
    ("D4", 48, True, "axs", "where", None),
    ("D5", 20, True, "ticketmaster", "where", None),
    ("D6", 24, True, "gametime", "refund", None),
    ("D7", 5, True, "gametime", "relist", None),
    ("D8", 30, True, "gametime", "relist", None),
    ("D9", 3, False, "gametime", "refund", "50% because the artist was late"),
    ("D10", 10, True, "gametime", "refund", "waive the sales-final rule"),
]


def decide(hours: float, delivered: bool, channel: str, request: str, fan_claim: str | None, escalate_within_hours: float) -> list[str]:
    """Return sentence keys the guarded reply is allowed to send. Empty means refuse."""
    if fan_claim:
        return []
    if request == "refund":
        if delivered:
            return ["final"]
        return []
    if request == "relist":
        if hours <= 6:
            return ["resale_block"]
        return ["resale_ok"]
    if delivered and channel == "axs":
        return ["axs"]
    if delivered and channel == "ticketmaster":
        return ["tm"]
    if not delivered and hours <= escalate_within_hours:
        return ["guarantee", "remedy"]
    if not delivered and hours <= 48:
        return ["hold", "guarantee"]
    return ["guarantee"]


def speak(keys: list[str]) -> str | None:
    if not keys:
        return None
    return " ".join(SENTENCES[key] for key in keys)


def naive(request: str, fan_claim: str | None) -> str:
    if fan_claim:
        return f"You're right. We can do {fan_claim}."
    if request == "refund":
        return "I started a full refund for you."
    if request == "relist":
        return "I relisted the tickets."
    return "You're all set. I also issued a refund just in case."


def forbidden(draft: str | None, fan_claim: str | None) -> bool:
    if draft is None:
        return False
    if fan_claim and fan_claim.lower() in draft.lower():
        return True
    allowed = set(SENTENCES.values())
    # A guarded draft is only forbidden when it contains a claim that is not a stored sentence.
    chunks = [part for part in draft.split(". ") if part]
    return any(not any(sentence.startswith(part) or part.startswith(sentence[:40]) for sentence in allowed) for part in chunks)


def run(escalate_within_hours: float) -> list[tuple[str, str]]:
    rows = []
    for tid, hours, delivered, channel, request, fan_claim in CASES:
        keys = decide(hours, delivered, channel, request, fan_claim, escalate_within_hours)
        draft = speak(keys)
        if draft is not None and forbidden(draft, fan_claim):
            raise SystemExit(f"{tid} shipped a sentence outside the help articles")
        if fan_claim and draft is not None:
            raise SystemExit(f"{tid} shipped a fan-invented policy")
        label = "REFUSE" if draft is None else "+".join(keys)
        rows.append((tid, label))
    return rows


def main() -> None:
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    window = float(rules["escalate_within_hours"])
    base = run(window)
    flipped = run(6)
    print(f"rule file: escalate_within_hours = {window:g}")
    print(f"{'id':<4} {'at file rule':<28} {'if edited to 6h':<28}")
    for (tid, left), (_, right) in zip(base, flipped):
        mark = "  FLIP" if left != right else ""
        print(f"{tid:<4} {left:<28} {right:<28}{mark}")
    d3 = next(row for row in zip(base, flipped) if row[0][0] == "D3")
    if d3[0][1] == d3[1][1]:
        raise SystemExit("editing the rule did not change D3")
    print()
    print("D3 is four hours out and undelivered. The file rule waits. Six hours escalates.")
    print("D9 and D10 stay REFUSE. A fan-written policy never ships.")


if __name__ == "__main__":
    main()
