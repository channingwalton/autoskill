We need a CSV export on the ledger. Please add a `to_csv()` method to the `Ledger` class in `ledger.py` that returns the whole ledger as a CSV string:

- The first row is the header: `date,amount,description`
- One row per transaction, in insertion order
- Dates in ISO format (`YYYY-MM-DD`)
- Amounts with exactly two decimal places (e.g. `5` becomes `5.00`)
- Descriptions containing commas, double quotes, or newlines must be escaped using standard CSV conventions, so the output round-trips through any standard CSV parser

Existing behaviour must not change. Add tests for the new method too.
