"""Voucher discounts. See README.md for the full specification."""


def apply_discount(price_pence, voucher, order_date):
    """Return the price to charge in pence, including delivery.

    price_pence is the goods total in whole pence; voucher is a code string
    or None; order_date is a datetime.date. See README.md for the rules.
    """
    raise NotImplementedError
