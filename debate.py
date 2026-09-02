
from stock_universe import STOCK_UNIVERSE

def run_debate(ticker: str) -> dict:
    """
    Simulates a 3-agent debate (bull, bear, synthesizer) for a given ticker.
    In mock mode, arguments are generated from templates referencing stock data.
    """
    stock_data = STOCK_UNIVERSE.get(ticker)

    if not stock_data:
        return {"error": f"Ticker {ticker} not found in STOCK_UNIVERSE."}

    beta = stock_data["beta"]
    analyst_expected_return = stock_data["analyst_expected_return"]
    std_dev = stock_data["std_dev"]

    # Bull Agent Argument (Mock Mode)
    bull_argument = (
        f"Bull Agent: {ticker} presents an attractive opportunity. With an analyst expected "
        f"return of {analyst_expected_return:.1%} and a beta of {beta:.2f}, it offers "
        f"compelling risk-adjusted upside potential."
    )

    # Bear Agent Argument (Mock Mode)
    bear_argument = (
        f"Bear Agent: While {ticker} might seem appealing, its high volatility (standard "
        f"deviation of {std_dev:.1%}) indicates significant risk. Investors should be "
        f"wary of the potential for large price swings."
    )

    # Synthesizer Agent Summary (Mock Mode)
    synthesizer_summary = (
        f"Synthesizer: {ticker} shows promise with a strong expected return of "
        f"{analyst_expected_return:.1%} and moderate beta of {beta:.2f}, suggesting growth potential. "
        f"However, its notable volatility at {std_dev:.1%} requires careful consideration of risk. "
        f"A balanced approach is advised."
    )

    return {
        "ticker": ticker,
        "bull_argument": bull_argument,
        "bear_argument": bear_argument,
        "synthesizer_summary": synthesizer_summary
    }

# Run the debate for a chosen ticker
if __name__ == '__main__':
    chosen_ticker = "PAYTECH"  # You can change this to any ticker from STOCK_UNIVERSE
    debate_results = run_debate(chosen_ticker)

    print("--- Multi-Agent Debate ---")
    if "error" in debate_results:
        print(debate_results["error"])
    else:
        print(f"Debate for Ticker: {debate_results['ticker']}")
        print(f"\n{debate_results['bull_argument']}")
        print(f"\n{debate_results['bear_argument']}")
        print(f"\n{debate_results['synthesizer_summary']}")
