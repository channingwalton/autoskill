# Voucher discounts

`apply_discount(price_pence, voucher, order_date)` returns the price the customer pays, in pence, as an `int`. `price_pence` is the goods total: always a whole, non-negative number of pence. `voucher` is a code string, or `None` when the customer has no voucher. `order_date` is always a `datetime.date` — the day the order is placed.

## Voucher codes

| Code      | Discount                                          |
|-----------|---------------------------------------------------|
| `SAVE10`  | 10% off orders over £50                           |
| `SAVE20`  | 20% off orders over £100                          |
| `FIVER`   | £5 off orders of £20 or more                      |
| `MIDWEEK` | £8 off orders of £40 or more, on weekdays only    |

Thresholds are exact: "over £50" means strictly more than £50.00, whereas "£20 or more" includes an order of exactly £20.00. A voucher whose conditions are not met gives no discount at all. An unrecognised voucher code is simply ignored, as is `None`.

Voucher codes are case-insensitive: `save10`, `Save10`, and `SAVE10` are the same voucher.

`MIDWEEK` is valid only when `order_date` falls on a weekday (Monday to Friday); on a Saturday or Sunday it gives no discount. Every other voucher, and the seasonal discount below, applies on any day.

## Automatic seasonal discount

Orders over £200 automatically receive 15% off — no voucher needed.

## Discounts never stack

At most one discount is ever applied to the goods. When more than one discount is available (for example the automatic seasonal discount plus a qualifying voucher), the customer gets whichever single discount takes the most money off — never both.

## Rounding

Percentage discounts can produce a fraction of a penny. Round the discounted goods total to the nearest whole penny, with exact half pennies rounding up: a computed total of 4504.5p becomes 4505p. The discounted goods total is never negative. Rounding happens before the delivery rule below is applied.

## Delivery

A flat £1.99 delivery charge is added to every order. Delivery is free when the **discounted** goods total — the amount after the chosen discount, not the original order value — is strictly over £25.00. The value returned by `apply_discount` always includes the delivery charge when one applies: discounted goods total plus delivery.
