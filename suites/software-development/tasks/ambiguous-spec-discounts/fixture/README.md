# Voucher discounts

`apply_discount(price_pence, voucher)` returns the price the customer pays, in pence, as an `int`. `price_pence` is always a whole, non-negative number of pence. `voucher` is a code string, or `None` when the customer has no voucher.

## Voucher codes

| Code     | Discount                       |
|----------|--------------------------------|
| `SAVE10` | 10% off orders over £50        |
| `SAVE20` | 20% off orders over £100       |
| `FIVER`  | £5 off orders of £20 or more   |

Thresholds are exact: "over £50" means strictly more than £50.00, whereas "£20 or more" includes an order of exactly £20.00. A voucher whose threshold is not met gives no discount at all. An unrecognised voucher code is simply ignored, as is `None`.

## Automatic seasonal discount

Orders over £200 automatically receive 15% off — no voucher needed.

## Discounts never stack

At most one discount is ever applied. When more than one discount is available (for example the automatic seasonal discount plus a qualifying voucher), the customer gets whichever single discount takes the most money off — never both.

## Rounding

Percentage discounts can produce a fraction of a penny. Round the final price to the nearest whole penny, with exact half pennies rounding up: a computed price of 4504.5p is charged as 4505p.

The returned price is never negative.
