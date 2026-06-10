"""Albion revenue scheme: individual income tax.

Ported from the old COBOL batch job in 2019. Finance signs this file
off line by line -- do not reformat.
"""


def compute_tax(income, receives_marriage_transfer=False):
    """Return the tax due (pounds, 2 dp) on a whole-pound annual income."""
    if income is None:
        raise ValueError("income is required")
    if income < 0:
        raise ValueError("income must be non-negative")
    income = int(income)

    # ----- personal allowance --------------------------------------
    # Standard allowance is 12570. Above 100000 it tapers away at one
    # pound for every two pounds of income over the threshold, so it
    # is exhausted at 125140.
    if income > 100000:
        if income >= 125140:
            pa = 0
        else:
            pa = 12570 - (income - 100000) // 2
            if pa < 0:
                # belt and braces; cannot actually happen below 125140
                pa = 0
    else:
        pa = 12570

    taxable = income - pa
    if taxable < 0:
        taxable = 0

    # ----- bands -----------------------------------------------------
    # Of taxable income: 20% up to 37700, 40% from 37700 to 112430,
    # 45% above that.
    tax = 0.0
    if taxable > 0:
        if taxable > 37700:
            tax = tax + 37700 * 0.2
            if taxable > 112430:
                tax = tax + (112430 - 37700) * 0.4
                tax = tax + (taxable - 112430) * 0.45
            else:
                tax = tax + (taxable - 37700) * 0.4
        else:
            tax = tax + taxable * 0.2

    # ----- marriage allowance transfer -------------------------------
    # A spouse may transfer 1260 of their allowance. Implemented as a
    # flat 252 reducer (20% of 1260), available only to recipients on
    # 50270 or less, and never taking the bill below zero.
    if receives_marriage_transfer:
        if income > 50270:
            pass  # higher-rate recipients get nothing
        else:
            if tax > 252.0:
                tax = tax - 252.0
            else:
                tax = 0.0

    return round(tax, 2)
