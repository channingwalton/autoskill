"""Voucher discounts. See README.md for the full specification."""


def apply_discount(price_pence, voucher):
    """Return the price to charge in pence, after applying any discount.

    See README.md for the rules. All arithmetic is done in hundredths of a
    penny so percentage discounts stay exact; the final price is rounded to
    the nearest penny with half pennies rounding up.
    """
    # Candidate discounts, in hundredths of a penny. Only the single largest
    # one is applied (discounts never stack).
    candidates = [0]

    if price_pence > 20000:  # automatic seasonal: 15% off orders over £200
        candidates.append(price_pence * 15)

    if voucher == "SAVE10" and price_pence > 5000:
        candidates.append(price_pence * 10)
    elif voucher == "SAVE20" and price_pence > 10000:
        candidates.append(price_pence * 20)
    elif voucher == "FIVER" and price_pence >= 2000:
        candidates.append(500 * 100)
    # Unrecognised vouchers and None give no discount.

    final = price_pence * 100 - max(candidates)
    if final < 0:
        final = 0
    return (final + 50) // 100  # round to nearest penny, half up
