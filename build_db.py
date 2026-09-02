"""
Build paytm_payments.db: a normalized SQLite database loaded from
merchants.xlsx, users.xlsx, and ledger.xlsx (source data supplied as
.xlsx workbooks rather than .csv -- same columns/content, so loaded
directly with pandas.read_excel instead of read_csv).

Schema:
    merchants(merchant_id PK, merchant_name, category, region)
    users(user_id PK, signup_date)
    transactions(transaction_id PK, user_id FK -> users, merchant_id FK -> merchants,
                 transaction_time, amount_inr, payment_method, status, risk_score)
"""
import sqlite3
import pandas as pd
import os

UPLOAD_DIR = "/mnt/user-data/uploads"
DB_PATH = "/home/claude/db_task/paytm_payments.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# ---------- 1. Load source data ----------
merchants = pd.read_excel(f"{UPLOAD_DIR}/merchants.xlsx")
users = pd.read_excel(f"{UPLOAD_DIR}/users.xlsx")
ledger = pd.read_excel(f"{UPLOAD_DIR}/ledger.xlsx")

# Normalize datetime columns to ISO strings so SQLite date/time functions
# (julianday, strftime) work directly on them.
users["signup_date"] = pd.to_datetime(users["signup_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
ledger["transaction_time"] = pd.to_datetime(ledger["transaction_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

# ---------- 2. Referential-integrity sanity check before loading ----------
missing_users = set(ledger["user_id"]) - set(users["user_id"])
missing_merchants = set(ledger["merchant_id"]) - set(merchants["merchant_id"])
assert not missing_users, f"ledger references unknown user_id(s): {missing_users}"
assert not missing_merchants, f"ledger references unknown merchant_id(s): {missing_merchants}"
assert merchants["merchant_id"].is_unique
assert users["user_id"].is_unique
assert ledger["transaction_id"].is_unique

# ---------- 3. Create schema ----------
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

cur.executescript("""
CREATE TABLE merchants (
    merchant_id     INTEGER PRIMARY KEY,
    merchant_name   TEXT NOT NULL,
    category        TEXT NOT NULL,
    region          TEXT NOT NULL
);

CREATE TABLE users (
    user_id         INTEGER PRIMARY KEY,
    signup_date     TEXT NOT NULL   -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
);

CREATE TABLE transactions (
    transaction_id   TEXT PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    merchant_id      INTEGER NOT NULL,
    transaction_time TEXT NOT NULL,  -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
    amount_inr       INTEGER NOT NULL,
    payment_method   TEXT NOT NULL,
    status           TEXT NOT NULL,
    risk_score       INTEGER NOT NULL,
    FOREIGN KEY (user_id)     REFERENCES users(user_id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

CREATE INDEX idx_txn_user      ON transactions(user_id);
CREATE INDEX idx_txn_merchant  ON transactions(merchant_id);
CREATE INDEX idx_txn_status    ON transactions(status);
CREATE INDEX idx_txn_time      ON transactions(transaction_time);
""")

# ---------- 4. Load data ----------
merchants[["merchant_id", "merchant_name", "category", "region"]].to_sql(
    "merchants", conn, if_exists="append", index=False
)
users[["user_id", "signup_date"]].to_sql(
    "users", conn, if_exists="append", index=False
)
ledger[["transaction_id", "user_id", "merchant_id", "transaction_time",
        "amount_inr", "payment_method", "status", "risk_score"]].to_sql(
    "transactions", conn, if_exists="append", index=False
)

conn.commit()

# ---------- 5. Verify row counts ----------
for tbl in ["merchants", "users", "transactions"]:
    n = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"{tbl}: {n} rows loaded")

# ---------- 6. Verify FK integrity from SQLite's own perspective ----------
cur.execute("PRAGMA foreign_key_check;")
violations = cur.fetchall()
print("foreign_key_check violations:", violations if violations else "none")

conn.close()
print(f"\nDatabase written to {DB_PATH}")
