"""Voucher discounts. See README.md for the full specification."""

DELIVERY_PENCE = 199
FREE_DELIVERY_OVER_PENCE = 2500


def apply_discount(price_pence, voucher, order_date):
    """Return the price to charge in pence, including delivery.

    price_pence is the goods total in whole pence; voucher is a code string
    or None; order_date is a datetime.date. See README.md for the rules.

    Discount arithmetic is done in hundredths of a penny so percentage
    discounts stay exact; the discounted goods total is rounded to the
    nearest penny (half pennies up) before the delivery rule is applied.
    """
    # Candidate discounts, in hundredths of a penny. Only the single
    # largest one is applied (discounts never stack).
    candidates = [0]

    if price_pence > 20000:  # automatic seasonal: 15% off orders over £200
        candidates.append(price_pence * 15)

    code = voucher.upper() if voucher is not None else None
    if code == "SAVE10" and price_pence > 5000:
        candidates.append(price_pence * 10)
    elif code == "SAVE20" and price_pence > 10000:
        candidates.append(price_pence * 20)
    elif code == "FIVER" and price_pence >= 2000:
        candidates.append(500 * 100)
    elif code == "MIDWEEK" and price_pence >= 4000 and order_date.weekday() < 5:
        candidates.append(800 * 100)
    # Unrecognised vouchers and None give no discount.

    goods_hundredths = price_pence * 100 - max(candidates)
    if goods_hundredths < 0:
        goods_hundredths = 0
    goods = (goods_hundredths + 50) // 100  # nearest penny, half up

    if goods > FREE_DELIVERY_OVER_PENCE:
        return goods
    return goods + DELIVERY_PENCE
