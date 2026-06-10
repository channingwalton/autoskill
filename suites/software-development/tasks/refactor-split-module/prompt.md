`shop.py` has grown into a grab-bag of unrelated concerns. Please split it into three modules:

- `pricing.py` — the price list, pricing constants, `unit_price`, `line_price`, and `add_vat`
- `basket.py` — the `Basket` class
- `report.py` — `format_pence`, `format_line`, and `format_receipt`

Keep `shop.py` as a thin compatibility shim that just re-exports the existing public API, so code doing `import shop` keeps working unchanged — after the split it should contain nothing but imports/re-exports (well under 30 lines).

Do not change any behaviour. The existing tests in `test_shop.py` must still pass.
