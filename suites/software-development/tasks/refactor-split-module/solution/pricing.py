"""Pricing rules and the price list (amounts in pence)."""

PRICES = {
    "apple": 60,
    "banana": 25,
    "milk": 130,
    "bread": 110,
    "cheese": 350,
}

BULK_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 10
VAT_PERCENT = 20


def unit_price(item):
    """Return the unit price of an item in pence."""
    try:
        return PRICES[item]
    except KeyError:
        raise KeyError(f"unknown item: {item!r}")


def line_price(item, quantity):
    """Price for a quantity of an item, with a bulk discount on 10 or more."""
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    total = unit_price(item) * quantity
    if quantity >= BULK_THRESHOLD:
        total -= total * BULK_DISCOUNT_PERCENT // 100
    return total


def add_vat(amount_pence):
    """Return the amount with VAT added (integer pence, rounded down)."""
    return amount_pence + amount_pence * VAT_PERCENT // 100
