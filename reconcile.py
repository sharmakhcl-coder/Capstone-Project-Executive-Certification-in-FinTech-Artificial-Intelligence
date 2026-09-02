"""
reconcile_payments(ledger_df, gateway_df)

Compares a payments ledger against the payment gateway's own export of the
same transactions and returns four DataFrames describing where they
disagree. Comparison key is `transaction_id`; set operations identify rows
present in only one file, and `pd.merge` (inner join) pairs up the rows
that exist in both so amount/status can be compared side by side.
"""
import pandas as pd


def reconcile_payments(ledger_df: pd.DataFrame, gateway_df: pd.DataFrame):
    """
    Parameters
    ----------
    ledger_df, gateway_df : DataFrame
        Each must contain at least: transaction_id, amount_inr, status.

    Returns
    -------
    missing_in_gateway : DataFrame
        Full ledger rows for transaction_ids present in the ledger but
        absent from the gateway export (the gateway never recorded them).
    missing_in_ledger : DataFrame
        Full gateway rows for transaction_ids present in the gateway
        export but absent from the ledger (extra transactions the ledger
        never recorded).
    amount_mismatches : DataFrame
        transaction_id + both amounts + a computed `amount_diff`
        (gateway - ledger) for transaction_ids present in both files
        whose amount_inr disagrees.
    status_mismatches : DataFrame
        transaction_id + both statuses for transaction_ids present in
        both files whose status disagrees.

    Notes
    -----
    A transaction can appear in both amount_mismatches and
    status_mismatches if both fields disagree -- the two DataFrames are
    independent discrepancy views, not a mutually-exclusive partition.
    """
    ledger_ids = set(ledger_df["transaction_id"])
    gateway_ids = set(gateway_df["transaction_id"])

    # ---- set operations on transaction_id ----
    missing_in_gateway_ids = ledger_ids - gateway_ids
    missing_in_ledger_ids = gateway_ids - ledger_ids

    missing_in_gateway = (
        ledger_df[ledger_df["transaction_id"].isin(missing_in_gateway_ids)]
        .copy()
        .reset_index(drop=True)
    )
    missing_in_ledger = (
        gateway_df[gateway_df["transaction_id"].isin(missing_in_ledger_ids)]
        .copy()
        .reset_index(drop=True)
    )

    # ---- pairwise comparison for transactions present in both ----
    common = pd.merge(
        ledger_df[["transaction_id", "amount_inr", "status"]],
        gateway_df[["transaction_id", "amount_inr", "status"]],
        on="transaction_id",
        how="inner",
        suffixes=("_ledger", "_gateway"),
    )

    amount_mismatches = common[
        common["amount_inr_ledger"] != common["amount_inr_gateway"]
    ].copy()
    amount_mismatches["amount_diff"] = (
        amount_mismatches["amount_inr_gateway"] - amount_mismatches["amount_inr_ledger"]
    )
    amount_mismatches = amount_mismatches[
        ["transaction_id", "amount_inr_ledger", "amount_inr_gateway", "amount_diff"]
    ].reset_index(drop=True)

    status_mismatches = common[
        common["status_ledger"] != common["status_gateway"]
    ][["transaction_id", "status_ledger", "status_gateway"]].reset_index(drop=True)

    return missing_in_gateway, missing_in_ledger, amount_mismatches, status_mismatches


if __name__ == "__main__":
    ledger = pd.read_excel("/mnt/user-data/uploads/ledger.xlsx")
    gateway = pd.read_excel("/mnt/user-data/uploads/gateway_export.xlsx")
    total_ledger = len(ledger)

    missing_in_gateway, missing_in_ledger, amount_mismatches, status_mismatches = (
        reconcile_payments(ledger, gateway)
    )

    print(f"Ledger transactions:  {len(ledger)}")
    print(f"Gateway transactions: {len(gateway)}\n")

    print(f"1. Missing in gateway export : {len(missing_in_gateway):3d}  "
          f"({len(missing_in_gateway)/total_ledger*100:.2f}% of ledger)")
    print(f"2. Missing in ledger (extra in gateway): {len(missing_in_ledger):3d}  "
          f"({len(missing_in_ledger)/total_ledger*100:.2f}% of ledger)")
    print(f"3. Amount mismatches         : {len(amount_mismatches):3d}  "
          f"({len(amount_mismatches)/total_ledger*100:.2f}% of ledger)")
    print(f"4. Status mismatches         : {len(status_mismatches):3d}  "
          f"({len(status_mismatches)/total_ledger*100:.2f}% of ledger)")

    print("\n--- Sample: missing_in_gateway (first 5) ---")
    print(missing_in_gateway.head().to_string())

    print("\n--- Sample: missing_in_ledger (first 5) ---")
    print(missing_in_ledger.head().to_string())

    print("\n--- amount_mismatches (all) ---")
    print(amount_mismatches.to_string())

    print("\n--- status_mismatches (all) ---")
    print(status_mismatches.to_string())
