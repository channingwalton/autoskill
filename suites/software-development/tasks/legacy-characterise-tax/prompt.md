tax.py computes income tax for our fictional Albion revenue scheme. It works in production, but it has no tests at all.

We need to change the personal-allowance taper soon, so please do two things:

1. Get the current behaviour under characterisation tests first.
2. Then make exactly this one change: above £100,000 the personal allowance should now reduce by £1 for every £3 of income over the threshold (it is currently £1 for every £2).

Nothing else about the calculation may change — the bands, the marriage allowance transfer, and the rounding must all behave exactly as they do today.
