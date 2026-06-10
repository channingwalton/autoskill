"""Stock auditing built on top of the shop API. Do not modify this module."""

import shop


def audit_value(stock):
    """Total value in pence of a {item: quantity} stock dict.

    Bulk discounts apply per line, exactly as in the shop.
    """
    return sum(shop.line_price(item, qty) for item, qty in sorted(stock.items()))


def insured_value(stock):
    """Replacement value of the stock including VAT."""
    return shop.add_vat(audit_value(stock))


def audit_report(stock):
    """Render a stock audit using the shop's receipt formatting."""
    lines = ["AUDIT"]
    for item, qty in sorted(stock.items()):
        lines.append(shop.format_line(item, qty, shop.line_price(item, qty)))
    lines.append("VALUE   " + shop.format_pence(audit_value(stock)))
    lines.append("INSURED " + shop.format_pence(insured_value(stock)))
    return "\n".join(lines)


def full_catalogue_value():
    """Value of one of everything in the price list."""
    return sum(shop.PRICES[item] for item in shop.PRICES)
