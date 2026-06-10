"""Compatibility shim: re-exports the shop public API from the split modules."""

from pricing import (
    BULK_DISCOUNT_PERCENT,
    BULK_THRESHOLD,
    PRICES,
    VAT_PERCENT,
    add_vat,
    line_price,
    unit_price,
)
from basket import Basket
from report import format_line, format_pence, format_receipt

__all__ = [
    "BULK_DISCOUNT_PERCENT",
    "BULK_THRESHOLD",
    "PRICES",
    "VAT_PERCENT",
    "add_vat",
    "line_price",
    "unit_price",
    "Basket",
    "format_line",
    "format_pence",
    "format_receipt",
]
