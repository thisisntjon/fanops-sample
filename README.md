# Fan-ops sample

Synthetic fan-ops exercise. No model call. The orders are invented. This is not a Gametime product and it contains no Gametime internal data.

## The gate

```
python fanops.py
```

The articles in `fanops.py` are invented. A naive drafter ships 4 policies those articles do not contain. The guarded drafter ships 8 replies copied from the articles and refuses 4.

## Ticket-delivery rescue

```
python delivery.py
```

The sentences in `delivery.py` are copied from Gametime's public help articles, with apostrophes normalized. A reply may contain only those sentences.

`rules.json` holds `escalate_within_hours`, set to 2. The run also prints the same cases at 6. D3 is four hours out and undelivered: the file rule waits on the barcode hold, and 6 hours escalates to the public remedy. D9 and D10 ask for a refund the articles do not allow. Both stay refused.

Sources:

- https://support.gametime.co/en_us/ticket-delivery-timeframe-BksQaxsnq
- https://support.gametime.co/en_us/ticket-resale-availability-ryqjJTT3c
- https://support.gametime.co/en_us/ticket-delivery-via-other-platforms-information-ByN2ZEV6q
