"""
Four-layer payments dashboard, rendered as saved chart images (matplotlib).

Data sources:
  ledger.xlsx      -- system-of-record transactions (547 rows), used for all
                      platform-wide metrics, trends, breakdowns, and the
                      per-merchant table.
  gateway_export.xlsx -- the payment gateway's own record of transactions,
                      used ONLY for the reconciliation match_rate scorecard.
  merchants.xlsx    -- merchant_id -> merchant_name / category / region.

All GMV figures (headline + trends + breakdown) are defined as the sum of
amount_inr for status == 'captured' transactions only, i.e. money that
actually settled -- the standard "GMV" definition in a payments context.
Success rate, chargeback ratio, and match rate are computed exactly per the
definitions given in the brief.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

OUT = "/home/claude/dashboard"

# ---------------------------------------------------------------- palette --
INK        = "#12232E"   # near-black text
NAVY       = "#1B4B5A"   # primary brand
TEAL       = "#2F8F9D"
GOLD       = "#C98A2C"   # warn accent
CORAL      = "#C64B4B"   # alert / chargeback accent
GREEN      = "#3E8E5A"   # success accent
PALE       = "#F4F6F5"   # panel background
GRID       = "#D9DEDD"
CAT_COLORS = ["#1B4B5A", "#2F8F9D", "#6FB3AE", "#C98A2C", "#C64B4B", "#7A6FA6", "#4C7A3F"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# ---------------------------------------------------------------- load ----
ledger = pd.read_excel("/mnt/user-data/uploads/ledger.xlsx")
gateway = pd.read_excel("/mnt/user-data/uploads/gateway_export.xlsx")
merchants = pd.read_excel("/mnt/user-data/uploads/merchants.xlsx")

ledger["transaction_time"] = pd.to_datetime(ledger["transaction_time"])
ledger["date"] = ledger["transaction_time"].dt.date

TOTAL_TXNS = len(ledger)
captured = ledger[ledger["status"] == "captured"]
chargebacks = ledger[ledger["status"] == "chargeback"]

# ---------------------------------------------------------------- headline metrics --
gmv_total = captured["amount_inr"].sum()
success_rate = len(captured) / TOTAL_TXNS * 100
chargeback_ratio = len(chargebacks) / TOTAL_TXNS * 100

merged_recon = ledger.merge(gateway, on="transaction_id", how="inner", suffixes=("_ledger", "_gateway"))
both_match = (
    (merged_recon["amount_inr_ledger"] == merged_recon["amount_inr_gateway"]) &
    (merged_recon["status_ledger"] == merged_recon["status_gateway"])
)
match_rate = both_match.sum() / len(ledger) * 100

print(f"GMV: INR {gmv_total:,.0f}")
print(f"Success rate: {success_rate:.2f}%")
print(f"Match rate: {match_rate:.2f}%  ({both_match.sum()} of {len(ledger)} ledger txns)")
print(f"Chargeback ratio: {chargeback_ratio:.2f}%")

# =====================================================================
# LAYER 1 -- HEADLINE SCORECARDS
# =====================================================================
scorecards = [
    ("TOTAL GMV", f"\u20b9{gmv_total:,.0f}", "Captured transactions, 1\u201330 Jan 2026", NAVY),
    ("SUCCESS RATE", f"{success_rate:.1f}%", f"{len(captured)} of {TOTAL_TXNS} transactions captured", GREEN),
    ("RECONCILIATION MATCH RATE", f"{match_rate:.1f}%", f"{both_match.sum()} of {len(ledger)} ledger txns match gateway on amount + status", TEAL),
    ("CHARGEBACK RATIO", f"{chargeback_ratio:.1f}%", f"{len(chargebacks)} of {TOTAL_TXNS} transactions", CORAL),
]

fig, axes = plt.subplots(1, 4, figsize=(15, 3.4))
fig.suptitle("Payments Dashboard \u2014 Headline Scorecards", fontsize=15, fontweight="bold", x=0.02, ha="left", color=INK)
for ax, (label, value, sub, color) in zip(axes, scorecards):
    ax.set_facecolor(PALE)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(0.86, xmin=0.06, xmax=0.94, color=color, linewidth=4, solid_capstyle="round")
    ax.text(0.08, 0.62, value, fontsize=27, fontweight="bold", color=color, transform=ax.transAxes, va="center")
    ax.text(0.08, 0.32, label, fontsize=10.5, fontweight="bold", color=INK, transform=ax.transAxes, va="center")
    ax.text(0.08, 0.12, sub, fontsize=8, color="#5B6B70", transform=ax.transAxes, va="center", wrap=True)
plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.savefig(f"{OUT}/1_headline_scorecards.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print("saved 1_headline_scorecards.png")

# =====================================================================
# LAYER 2 -- TRENDS: daily GMV + daily chargeback count over the 30-day window
# =====================================================================
full_range = pd.date_range("2026-01-01", "2026-01-30", freq="D").date
daily_gmv = captured.groupby("date")["amount_inr"].sum().reindex(full_range, fill_value=0)
daily_cb = chargebacks.groupby("date").size().reindex(full_range, fill_value=0)

fig, ax1 = plt.subplots(figsize=(13, 5))
ax1.set_title("Daily GMV vs. Chargeback Count \u2014 1\u201330 Jan 2026", fontsize=14, fontweight="bold", loc="left", pad=14)

x = range(len(full_range))
xlabels = [d.strftime("%d %b") for d in full_range]

ax1.plot(x, daily_gmv.values, color=NAVY, linewidth=2.2, marker="o", markersize=3.5, label="Daily GMV (\u20b9, captured)")
ax1.fill_between(x, daily_gmv.values, color=NAVY, alpha=0.08)
ax1.set_ylabel("Daily GMV (\u20b9)", color=NAVY, fontweight="bold")
ax1.tick_params(axis="y", labelcolor=NAVY)
ax1.set_xticks(x[::2])
ax1.set_xticklabels([xlabels[i] for i in x[::2]], rotation=45, ha="right", fontsize=8.5)
ax1.grid(axis="y", color=GRID, linewidth=0.7)
ax1.set_axisbelow(True)
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)

ax2 = ax1.twinx()
ax2.bar(x, daily_cb.values, color=CORAL, alpha=0.55, width=0.5, label="Daily chargeback count")
ax2.set_ylabel("Chargeback count", color=CORAL, fontweight="bold")
ax2.tick_params(axis="y", labelcolor=CORAL)
ax2.set_ylim(0, max(daily_cb.values.max() * 3, 5))
for spine in ["top"]:
    ax2.spines[spine].set_visible(False)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=9.5)

plt.tight_layout()
plt.savefig(f"{OUT}/2_trends_daily_gmv_chargebacks.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print("saved 2_trends_daily_gmv_chargebacks.png")

# =====================================================================
# LAYER 3 -- BREAKDOWN: GMV by payment_method and by category
# =====================================================================
by_pm = captured.groupby("payment_method")["amount_inr"].sum().sort_values(ascending=False)

merged_cat = ledger.merge(merchants[["merchant_id", "category"]], on="merchant_id", how="left")
by_cat = merged_cat[merged_cat["status"] == "captured"].groupby("category")["amount_inr"].sum().sort_values(ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Captured GMV Breakdown", fontsize=14, fontweight="bold", x=0.02, ha="left")

bars1 = ax1.bar(by_pm.index, by_pm.values, color=CAT_COLORS[:len(by_pm)], width=0.6)
ax1.set_title("By payment method", fontsize=11.5, loc="left", color="#5B6B70")
ax1.set_ylabel("GMV (\u20b9)")
ax1.grid(axis="y", color=GRID, linewidth=0.7)
ax1.set_axisbelow(True)
for spine in ["top", "right"]:
    ax1.spines[spine].set_visible(False)
for b in bars1:
    h = b.get_height()
    ax1.text(b.get_x() + b.get_width()/2, h + max(by_pm.values)*0.015, f"\u20b9{h:,.0f}",
              ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK)

bars2 = ax2.bar(by_cat.index, by_cat.values, color=CAT_COLORS[:len(by_cat)], width=0.6)
ax2.set_title("By merchant category", fontsize=11.5, loc="left", color="#5B6B70")
ax2.grid(axis="y", color=GRID, linewidth=0.7)
ax2.set_axisbelow(True)
ax2.tick_params(axis="x", rotation=30)
plt.setp(ax2.get_xticklabels(), ha="right")
for spine in ["top", "right"]:
    ax2.spines[spine].set_visible(False)
for b in bars2:
    h = b.get_height()
    ax2.text(b.get_x() + b.get_width()/2, h + max(by_cat.values)*0.015, f"\u20b9{h:,.0f}",
              ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f"{OUT}/3_breakdown_gmv.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print("saved 3_breakdown_gmv.png")
print(by_pm)
print(by_cat)

# =====================================================================
# LAYER 4 -- DETAILS: top 10 merchants by transaction count, table image
# with a `flag` column for per-merchant chargeback_ratio > 1%
# =====================================================================
merch_stats = ledger.groupby("merchant_id").agg(
    txn_count=("transaction_id", "count"),
    chargeback_count=("status", lambda s: (s == "chargeback").sum()),
).reset_index()
merch_stats["chargeback_ratio_pct"] = merch_stats["chargeback_count"] / merch_stats["txn_count"] * 100
merch_stats = merch_stats.merge(merchants, on="merchant_id", how="left")
merch_stats["flag"] = merch_stats["chargeback_ratio_pct"].apply(lambda r: "\u26a0 High CB" if r > 1 else "OK")

top10 = merch_stats.sort_values("txn_count", ascending=False).head(10).reset_index(drop=True)

cols = ["merchant_id", "merchant_name", "category", "region", "txn_count", "chargeback_count", "chargeback_ratio_pct", "flag"]
col_labels = ["Merchant ID", "Merchant", "Category", "Region", "Txn Count", "Chargebacks", "CB Ratio %", "Flag"]

cell_text = []
for _, row in top10.iterrows():
    cell_text.append([
        str(row["merchant_id"]),
        row["merchant_name"],
        row["category"],
        row["region"],
        str(row["txn_count"]),
        str(row["chargeback_count"]),
        f"{row['chargeback_ratio_pct']:.1f}%",
        row["flag"],
    ])

fig, ax = plt.subplots(figsize=(12.5, 0.40 * len(top10) + 1.0))
ax.axis("off")
ax.set_title("Top 10 Merchants by Transaction Count", fontsize=14, fontweight="bold", loc="left", pad=10, y=1.02)

table = ax.table(cellText=cell_text, colLabels=col_labels, loc="center", cellLoc="center", bbox=[0, 0.06, 1, 0.9])
table.auto_set_font_size(False)
table.set_fontsize(9.5)

for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor(NAVY)
    cell.set_text_props(color="white", fontweight="bold")
    cell.set_edgecolor("white")

flagged_rows = []
for i, row in top10.iterrows():
    is_flagged = row["chargeback_ratio_pct"] > 1
    if is_flagged:
        flagged_rows.append(i + 1)
    for j in range(len(col_labels)):
        cell = table[i + 1, j]
        cell.set_edgecolor(GRID)
        if is_flagged:
            cell.set_facecolor("#FBE3E3")
            if j == len(col_labels) - 1:
                cell.set_text_props(color=CORAL, fontweight="bold")
        else:
            cell.set_facecolor("white" if i % 2 == 0 else "#F7F9F9")
            if j == len(col_labels) - 1:
                cell.set_text_props(color=GREEN, fontweight="bold")

fig.text(0.02, 0.01, f"Flagged: chargeback_ratio (count-based, per merchant) > 1%  \u2014  {len(flagged_rows)} of 10 merchants shown flagged.",
          fontsize=9, color="#5B6B70")

plt.savefig(f"{OUT}/4_details_top10_merchants.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print("saved 4_details_top10_merchants.png")
print(top10[cols])
