"""Receipt formatting."""


def format_pence(pence):
    """Format integer pence as pounds, e.g. 130 -> '£1.30'."""
    return f"£{pence // 100}.{pence % 100:02d}"


def format_line(item, quantity, price_pence):
    """Format one receipt line."""
    return f"{quantity:>3} x {item:<12}{format_pence(price_pence):>8}"


def format_receipt(basket):
    """Render a basket as a printable receipt."""
    lines = ["RECEIPT"]
    for item, qty, price in basket.lines():
        lines.append(format_line(item, qty, price))
    lines.append("SUBTOTAL " + format_pence(basket.subtotal()))
    lines.append("TOTAL    " + format_pence(basket.total_with_vat()))
    return "\n".join(lines)
