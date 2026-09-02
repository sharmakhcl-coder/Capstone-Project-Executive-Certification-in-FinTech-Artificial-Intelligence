# Payments Dashboard — Interpretation

**Data window:** 1–30 Jan 2026 · **Source of truth:** `ledger.xlsx` (547 transactions), cross-checked against `gateway_export.xlsx` (530 transactions) for reconciliation. Merchant attributes joined from `merchants.xlsx`.

**Definitions used throughout:** GMV = sum of `amount_inr` for `status == 'captured'` transactions only (money that actually settled). Success rate, chargeback ratio, and match rate follow the exact count-based definitions specified in the brief.

## 1. Headline scorecards

| Metric | Value | Basis |
|---|---|---|
| Total GMV | ₹290,382 | 468 captured transactions |
| Success rate | 85.6% | 468 / 547 |
| Reconciliation match rate | 90.5% | 495 / 547 ledger txns match the gateway export on **both** amount and status |
| Chargeback ratio | 5.1% | 28 / 547 |

The 9.5-point gap between success rate (85.6%) and match rate (90.5%) is worth noting on its own: they are different failure modes. Success rate says roughly 1 in 7 transactions never captured. Match rate says roughly 1 in 10 transactions the ledger has on record don't agree with the gateway's own copy of that same transaction (27 transactions the ledger has that the gateway export is missing entirely, 10 the gateway has that the ledger is missing, and 26 of the 520 transactions both systems share disagree on amount and/or status). That reconciliation gap is a data-integrity problem independent of whether the underlying payment succeeded.

## 2. Trends — daily GMV vs. daily chargebacks

Daily GMV is volatile day to day (a low of ~₹2,200 on Jan 7 to a high of ~₹22,990 on Jan 11), with no obvious weekly seasonality pattern in this window. Chargebacks are sparse most days (0–2) but cluster later in the month: Jan 23 (4 chargebacks) and Jan 29 (3) are the two most visibly elevated days, with a generally heavier chargeback presence across Jan 21–29 than the first half of the month. That back-half concentration is the kind of pattern worth a follow-up look — e.g. whether it lines up with a specific merchant, cohort, or promotion that ran in the second half of January.

## 3. Breakdown — GMV by payment method and by category

**By payment method:** UPI dominates captured GMV (₹158,895 — more than the other three methods combined), followed by Wallet (₹56,863), Card (₹42,624), and Netbanking (₹32,000). Any UPI-specific outage or rule change would have an outsized revenue impact relative to the other rails.

**By merchant category:** Travel (₹59,759), grocery (₹59,398), and ecommerce (₹58,466) are closely bunched at the top and together account for over 60% of captured GMV; food_delivery and entertainment form a mid tier; bill_payment and recharge are the smallest categories by GMV, consistent with those being lower-ticket, high-frequency use cases rather than high-value ones.

## 4. Details — top 10 merchants by transaction count

7 of the top 10 merchants by transaction volume exceed the 1% per-merchant chargeback-ratio threshold (flagged in the table). Two stand out sharply: **Merchant_027** (18.8% chargeback ratio, 3 of 16 transactions) and **Merchant_029** (15.8%, 3 of 19) — both ecommerce merchants in the North region. Their chargeback ratios are 3–4x higher than the platform-wide 5.1% baseline, despite being high-volume, "trusted-by-traffic" merchants. That combination — high transaction count *and* high chargeback ratio — is exactly the pattern worth prioritizing for merchant risk review, since it affects more customers per merchant than a low-volume merchant with the same ratio would.

The three merchants that stay under the 1% threshold (Merchant_016, Merchant_009, Merchant_030) span bill_payment, ecommerce, and travel — so a clean chargeback record isn't concentrated in any one category among this top-10 set.

## Caveats

- GMV, the payment-method breakdown, and the category breakdown all use **captured-only** amounts, consistent with a standard GMV definition; if a "gross of all attempts" figure is wanted instead, that's a one-line filter change (documented in `build_dashboard.py`).
- The reconciliation figures here reflect only the single `match_rate` headline number as defined in this brief — the four discrepancy categories referenced from `reconcile_payments()` (Part C) are a separate, unaffected calculation not reproduced in this dashboard.
- Two ledger transactions carry negative `amount_inr` values (likely refund/data artifacts, ₹-51 and ₹-1); they are included as-is in all sums since no cleansing instruction was given, and their effect on the totals above is negligible (≤₹52 combined).
