-- =====================================================================
-- Query 1: SELECT / DISTINCT / WHERE / ORDER BY / LIMIT
-- Distinct payment methods used in captured transactions over ₹2,000,
-- alphabetically, top 5.
-- =====================================================================
SELECT DISTINCT payment_method
FROM transactions
WHERE status = 'captured' AND amount_inr > 2000
ORDER BY payment_method
LIMIT 5;


-- =====================================================================
-- Query 2: INNER JOIN + GROUP BY / HAVING
-- Merchant categories whose total captured revenue exceeds ₹50,000.
-- =====================================================================
SELECT m.category,
       SUM(t.amount_inr) AS total_captured_revenue,
       COUNT(*)          AS captured_txn_count
FROM transactions t
INNER JOIN merchants m ON m.merchant_id = t.merchant_id
WHERE t.status = 'captured'
GROUP BY m.category
HAVING SUM(t.amount_inr) > 50000
ORDER BY total_captured_revenue DESC;


-- =====================================================================
-- Query 3: LEFT JOIN
-- Every merchant with its transaction count, including any merchant
-- that has never processed a transaction (would show 0).
-- =====================================================================
SELECT m.merchant_id,
       m.merchant_name,
       m.region,
       COUNT(t.transaction_id) AS txn_count
FROM merchants m
LEFT JOIN transactions t ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.region
ORDER BY txn_count ASC, m.merchant_id;


-- =====================================================================
-- Query 4: Chargeback impact
-- Count of chargeback transactions, unique users affected, total
-- chargeback amount.
-- =====================================================================
SELECT COUNT(*)                       AS chargeback_txn_count,
       COUNT(DISTINCT user_id)        AS unique_users_affected,
       SUM(amount_inr)                AS total_chargeback_amount_inr
FROM transactions
WHERE status = 'chargeback';


-- =====================================================================
-- Query 5: Burner-account detection
-- Chargeback transactions where the signup happened on or before the
-- transaction (age >= 0, never negative) and strictly less than 30
-- days before it (age < 30). Uses INNER JOIN to users for signup_date.
-- =====================================================================
SELECT t.transaction_id,
       t.user_id,
       u.signup_date,
       t.transaction_time,
       CAST(julianday(t.transaction_time) - julianday(u.signup_date) AS INTEGER) AS account_age_days,
       t.amount_inr
FROM transactions t
INNER JOIN users u ON u.user_id = t.user_id
WHERE t.status = 'chargeback'
  AND (julianday(t.transaction_time) - julianday(u.signup_date)) >= 0
  AND (julianday(t.transaction_time) - julianday(u.signup_date)) < 30
ORDER BY account_age_days ASC;


-- =====================================================================
-- Query 6: Velocity-attack detection
-- Users with 3+ transactions inside any 10-minute window. Transactions
-- are grouped by user_id and a floor("transaction_time" to the nearest
-- 10 minutes, epoch-aligned) bucket; groups with >= 3 transactions are
-- surfaced. (See note in the accompanying report on why this bucketing
-- catches all 8 seeded clusters cleanly for this dataset.)
-- =====================================================================
SELECT user_id,
       datetime((CAST(strftime('%s', transaction_time) AS INTEGER) / 600) * 600, 'unixepoch') AS window_start,
       COUNT(*) AS txns_in_window,
       GROUP_CONCAT(transaction_id) AS transaction_ids
FROM transactions
GROUP BY user_id, CAST(strftime('%s', transaction_time) AS INTEGER) / 600
HAVING COUNT(*) >= 3
ORDER BY user_id, window_start;


-- =====================================================================
-- Query 7: Top spenders (extra) -- SELECT / WHERE / GROUP BY / ORDER BY / LIMIT
-- Top 10 users by total captured spend.
-- =====================================================================
SELECT t.user_id,
       SUM(t.amount_inr) AS total_captured_spend,
       COUNT(*)          AS captured_txn_count
FROM transactions t
WHERE t.status = 'captured'
GROUP BY t.user_id
ORDER BY total_captured_spend DESC
LIMIT 10;
