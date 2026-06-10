We need a CSV export on the ledger. Please add a `to_csv()` method to the `Ledger` class in `ledger.py` that returns the whole ledger as a CSV string:

- The first row is the header: `date,amount,description`
- One row per transaction, strictly in insertion order (do not sort)
- Dates in ISO format (`YYYY-MM-DD`)
- Amounts with exactly two decimal places (e.g. `5` becomes `5.00`, `0` becomes `0.00`)
- Descriptions must round-trip through any standard CSV parser exactly as stored, per RFC 4180 conventions: commas, double quotes, and embedded newlines must be quoted/escaped, and leading or trailing spaces in a description must be preserved, never trimmed
- Rows are terminated with `\n` (LF) — not `\r\n` — and the string ends with exactly one trailing newline after the last row
- An empty ledger exports as the header row only, so the result is exactly `"date,amount,description\n"`
- Calling `to_csv()` must not modify the ledger; calling it twice gives the same string

Existing behaviour must not change. Add tests for the new method too.
