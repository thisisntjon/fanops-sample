"""Synthetic fan-ops loop: retrieve, draft, and refuse anything the article did not say.

No network. No employer data. The tickets are invented. Run: python fanops.py
"""

from __future__ import annotations

import re

ARTICLES = {
    "transfer": (
        "A mobile transfer can take up to 2 hours. "
        "If the event starts in under 2 hours and the ticket has not arrived, a person takes the case."
    ),
    "refund": (
        "A refund is issued only when the organizer cancels the event, or the fan paid and the ticket was never delivered. "
        "Artist timing, set length, and seat view are not refund reasons."
    ),
    "seller": (
        "If the seller has not sent the transfer within 3 hours of the sale, Fan Ops contacts the seller. "
        "Do not promise a replacement ticket before that window ends."
    ),
    "exchange": (
        "An unused ticket can be exchanged for another listed event up to 24 hours before the original start time."
    ),
}

# (id, fan text, article id or None, phrase the fan wants repeated that the article does not contain)
TICKETS = [
    ("01", "My transfer still is not here. The show is in four hours.", "transfer", None),
    ("02", "The doors are in 30 minutes and the ticket never arrived.", "transfer", None),
    ("03", "The organizer canceled. I want the refund your article describes.", "refund", None),
    ("04", "I paid and the ticket was never delivered.", "refund", None),
    ("05", "The seller has not transferred and it has been an hour.", "seller", None),
    ("06", "It has been 4 hours and the seller still has not sent it.", "seller", None),
    ("07", "I want to exchange this unused ticket. The event is in three days.", "exchange", None),
    ("08", "Can I exchange? The event starts in 6 hours.", "exchange", None),
    ("09", "Your policy is a 50% refund anytime the artist goes on late.", "refund", "50% refund anytime"),
    ("10", "Just send a new ticket now. Do not wait the 3 hours.", "seller", "a new ticket now"),
    ("11", "Waive the 24-hour exchange rule. I am already in the car.", "exchange", "waive the 24-hour rule"),
    ("12", "Give me the CEO's mobile number.", None, "the CEO's mobile number"),
]


def retrieve(text: str) -> str | None:
    # The article id is chosen from the fan's words, not from a model.
    keys = {
        "transfer": ("transfer", "arrived", "doors"),
        "refund": ("refund", "canceled", "cancel", "delivered", "artist"),
        "seller": ("seller",),
        "exchange": ("exchange",),
    }
    best, score = None, 0
    for key, words in keys.items():
        hit = sum(re.search(rf"\b{re.escape(word)}\b", text.lower()) is not None for word in words)
        if hit > score:
            best, score = key, hit
    return best if score else None


def naive_draft(text: str, article_id: str | None, fan_claim: str | None) -> str:
    """What an unguarded drafter does: agree with the fan when they state a policy."""
    if fan_claim:
        return f"You're right. We can do {fan_claim}."
    if article_id is None:
        return "I don't have an article for that, but I can make an exception."
    return ARTICLES[article_id]


def guarded_draft(article_id: str | None, fan_claim: str | None) -> str | None:
    """Ship a reply only when every sentence is copied from the retrieved article."""
    if article_id is None or fan_claim:
        return None
    return ARTICLES[article_id]


def grounded(draft: str | None, article_id: str | None) -> bool:
    if draft is None:
        return True
    if article_id is None:
        return False
    return draft == ARTICLES[article_id]


def main() -> None:
    naive_false = 0
    guarded_shipped = 0
    guarded_refused = 0
    print(f"{'id':<4} {'route':<10} {'naive':<12} {'guarded':<10}")
    for tid, text, _expected, fan_claim in TICKETS:
        article_id = retrieve(text)
        naive = naive_draft(text, article_id, fan_claim)
        guarded = guarded_draft(article_id, fan_claim)
        naive_ok = grounded(naive, article_id)
        if not naive_ok:
            naive_false += 1
        if guarded is None:
            guarded_refused += 1
            guarded_label = "REFUSE"
        else:
            guarded_shipped += 1
            guarded_label = "SHIP"
        print(f"{tid:<4} {(article_id or 'none'):<10} {('ok' if naive_ok else 'FALSE'):<12} {guarded_label:<10}")
    print()
    print(f"naive false ships: {naive_false}")
    print(f"guarded shipped:   {guarded_shipped}")
    print(f"guarded refused:   {guarded_refused}")
    if naive_false != 4 or guarded_shipped != 8 or guarded_refused != 4:
        raise SystemExit("scorecard drifted from the letter")


if __name__ == "__main__":
    main()
