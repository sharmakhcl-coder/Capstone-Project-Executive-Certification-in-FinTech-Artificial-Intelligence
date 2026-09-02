
import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN
from investor_profiles import INVESTOR_PROFILES

# Correlation coefficient for portfolio variance calculation
PAIRWISE_CORRELATION = 0.3

# --- Act Stage: Tool call simulation ---
def get_stock_data(ticker: str) -> dict:
    """Simulates an external API call to get stock data."""
    return STOCK_UNIVERSE.get(ticker)

# --- Think Stage: Determine allocation based on risk tolerance ---
def determine_allocation(risk_tolerance: str) -> list:
    """Determines the stock allocation based on the investor's risk tolerance."""
    if risk_tolerance == "Conservative":
        return ["PAYBOND", "PAYGOLD", "PAYRETAIL"]
    elif risk_tolerance == "Moderate":
        return ["PAYRETAIL", "PAYINFRA", "PAYGOLD"]
    elif risk_tolerance == "Aggressive":
        return ["PAYTECH", "PAYFIN", "PAYINFRA"]
    else:
        raise ValueError(f"Unknown risk tolerance: {risk_tolerance}")

# --- Observe -> Decide Stage: Compute portfolio metrics ---
def compute_portfolio_metrics(tickers: list) -> tuple:
    """Computes portfolio expected return and standard deviation."""
    if len(tickers) != 3:
        raise ValueError("Allocation must be exactly 3 tickers for this calculation.")

    # Equal weight for each stock
    weight = 1 / len(tickers)

    portfolio_expected_return = 0
    portfolio_variance = 0
    stock_data = {}

    # Fetch data and calculate individual expected returns (CAPM)
    for ticker in tickers:
        data = get_stock_data(ticker)
        if not data:
            raise ValueError(f"Stock data not found for ticker: {ticker}")
        stock_data[ticker] = data

        # CAPM: E(R) = R_f + beta * (E(R_m) - R_f)
        stock_capm_return = RISK_FREE_RATE + data["beta"] * (MARKET_RETURN - RISK_FREE_RATE)
        portfolio_expected_return += weight * stock_capm_return

        # Add variance component for each stock: w_i^2 * sigma_i^2
        portfolio_variance += (weight ** 2) * (data["std_dev"] ** 2)

    # Add covariance component for each pair: 2 * w_i * w_j * Cov(R_i, R_j)
    # Cov(R_i, R_j) = rho * sigma_i * sigma_j
    # For 3 tickers, there are 3 pairs (i, j) where i < j: (0,1), (0,2), (1,2)
    ticker_list = list(stock_data.keys())
    for i in range(len(ticker_list)):
        for j in range(i + 1, len(ticker_list)):
            ticker_i = ticker_list[i]
            ticker_j = ticker_list[j]
            std_dev_i = stock_data[ticker_i]["std_dev"]
            std_dev_j = stock_data[ticker_j]["std_dev"]

            covariance = PAIRWISE_CORRELATION * std_dev_i * std_dev_j
            portfolio_variance += 2 * weight * weight * covariance

    portfolio_std_dev = math.sqrt(portfolio_variance)
    return portfolio_expected_return, portfolio_std_dev

# --- Agent Loop ---
def run_advisory_agent(investor_profile: dict) -> dict:
    """
    Runs the portfolio advisory agent for a given investor profile.
    Returns a dictionary with recommendation details or an escalation flag.
    """
    investor_id = investor_profile["investor_id"]
    risk_tolerance = investor_profile["risk_tolerance"]

    # 1. Think: Determine allocation
    recommended_tickers = determine_allocation(risk_tolerance)

    # 2. Act: Get stock data and compute portfolio metrics
    expected_return, std_dev = compute_portfolio_metrics(recommended_tickers)

    # 3. Observe -> Decide: Check for escalation and finalize recommendation
    if std_dev > 0.20: # 20%
        return {
            "investor_id": investor_id,
            "risk_tolerance": risk_tolerance,
            "ESCALATED_TO_HUMAN_ADVISOR": True,
            "recommended_tickers": recommended_tickers,
            "expected_portfolio_return": expected_return,
            "portfolio_standard_deviation": std_dev
        }
    else:
        # MOCK_LLM = 1 baseline: f-string template
        narrative = (
            f"For {risk_tolerance} investor {investor_id}, we recommend an allocation across "
            f"{', '.join(recommended_tickers)} with an expected portfolio return of "
            f"{expected_return:.1%} and volatility of {std_dev:.1%}."
        )
        return {
            "investor_id": investor_id,
            "risk_tolerance": risk_tolerance,
            "ESCALATED_TO_HUMAN_ADVISOR": False,
            "recommended_tickers": recommended_tickers,
            "expected_portfolio_return": expected_return,
            "portfolio_standard_deviation": std_dev,
            "recommendation_narrative": narrative
        }

# --- Run for all investor profiles ---
if __name__ == '__main__':
    results = []
    for profile in INVESTOR_PROFILES:
        result = run_advisory_agent(profile)
        results.append(result)
        print(f"\nResult for {profile['investor_id']}:")
        print(result)

    print("\n--- Summary of all recommendations ---")
    for res in results:
        if res.get("ESCALATED_TO_HUMAN_ADVISOR"):
            print(f"Investor {res['investor_id']} ({res['risk_tolerance']}): ESCALATED (Std Dev: {res['portfolio_standard_deviation']:.1%})")
        else:
            print(f"Investor {res['investor_id']} ({res['risk_tolerance']}): {res['recommendation_narrative']}")
