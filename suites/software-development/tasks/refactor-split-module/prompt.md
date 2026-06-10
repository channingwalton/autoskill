`shop.py` has grown into a grab-bag of unrelated concerns. Please split it into three modules:

- `pricing.py` — the price list, pricing constants, `unit_price`, `line_price`, and `add_vat`
- `basket.py` — the `Basket` class
- `report.py` — `format_pence`, `format_line`, and `format_receipt`

Keep `shop.py` as a thin compatibility shim that just re-exports the existing public API, so code doing `import shop` keeps working unchanged — other modules in this repo import `shop` and must not need editing. After the split, `shop.py` should contain nothing but imports/re-exports (no `def` or `class` statements; well under 30 lines). Re-export means the same objects: `shop.PRICES` must be the very dict `pricing.PRICES`, not a copy.

Dependencies must point one way only: `report.py` may import `basket`/`pricing`, `basket.py` may import `pricing`, and `pricing.py` must import neither — running `python3 -c "import pricing"` must not load `basket` or `report` as a side effect.

Do not change any behaviour. All existing tests (`test_shop.py`, `test_audit.py`) must still pass.
