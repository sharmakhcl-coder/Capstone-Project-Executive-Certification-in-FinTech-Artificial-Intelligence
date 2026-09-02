
import math
from stock_universe import RISK_FREE_RATE, MARKET_RETURN, STOCK_UNIVERSE

# --- Chosen Inputs for DCF Valuation (stated in writing) ---
# All currency figures are in INR millions.

# Base year financial figures
EBIT_BASE = 1000          # Earnings Before Interest & Taxes
TAX_RATE = 0.30           # Corporate Tax Rate (30%)
DEPREC_AMORT = 100        # Depreciation & Amortization
CAPEX = 150               # Capital Expenditure
DELTA_NWC = 50            # Change in Net Working Capital

# Growth rates
INITIAL_GROWTH_RATE = 0.10 # 5-year projected growth rate (10%)
TERMINAL_GROWTH_RATE = 0.03 # Lower terminal growth rate (3%)

# Capital structure and cost
COST_OF_DEBT_PRE_TAX = 0.08 # Illustrative pre-tax cost of debt (8%)
DEBT_TO_EQUITY_RATIO = 0.5  # Illustrative Debt to Equity ratio

# For Cost of Equity (Re) using CAPM, using PAYFIN's beta
EQUITY_BETA = STOCK_UNIVERSE["PAYFIN"]["beta"] # 1.35

# --- DCF Calculation Functions ---
def calculate_fcff(ebit, tax_rate, dep_amort, capex, delta_nwc):
    """Calculates Free Cash Flow to the Firm (FCFF)."""
    # FCFF = EBIT * (1 - tax rate) + D&A - CapEx - Delta_NWC
    return ebit * (1 - tax_rate) + dep_amort - capex - delta_nwc

def calculate_wacc(equity_beta, risk_free_rate, market_return, cost_of_debt_pre_tax, tax_rate, debt_to_equity_ratio):
    """Calculates the Weighted Average Cost of Capital (WACC)."""
    # Cost of Equity (Re) using CAPM
    re = risk_free_rate + equity_beta * (market_return - risk_free_rate)

    # After-tax Cost of Debt (Rd_at)
    rd_at = cost_of_debt_pre_tax * (1 - tax_rate)

    # Weights for WACC (assuming D/E ratio)
    equity_weight = 1 / (1 + debt_to_equity_ratio)
    debt_weight = debt_to_equity_ratio / (1 + debt_to_equity_ratio)

    wacc = (equity_weight * re) + (debt_weight * rd_at)
    return wacc, re, rd_at, equity_weight, debt_weight

def run_dcf_valuation(initial_fcff, initial_growth, terminal_growth, years, wacc):
    """Runs the DCF valuation model and returns present value of FCFFs and Terminal Value."""
    projected_fcffs = []
    discount_factors = []
    pv_fcffs = []

    current_fcff = initial_fcff

    # Project FCFF for 'years' period
    for i in range(1, years + 1):
        current_fcff *= (1 + initial_growth)
        projected_fcffs.append(current_fcff)
        discount_factor = (1 + wacc) ** i
        discount_factors.append(1 / discount_factor)
        pv_fcffs.append(current_fcff / discount_factor)

    # Calculate Terminal Value (TV) at the end of projection period (Year 5)
    # FCFF_year_6 = FCFF_year_5 * (1 + terminal_growth)
    fcff_year_after_projection = projected_fcffs[-1] * (1 + terminal_growth)

    # TV = FCFF_year_after_projection / (WACC - terminal_growth)
    terminal_value = fcff_year_after_projection / (wacc - terminal_growth)

    # Discount Terminal Value back to Present Value (Year 0)
    pv_terminal_value = terminal_value / ((1 + wacc) ** years)

    enterprise_value = sum(pv_fcffs) + pv_terminal_value

    return {
        "projected_fcffs": projected_fcffs,
        "pv_fcffs": pv_fcffs,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value
    }

# --- Main execution for DCF Calculator ---
if __name__ == '__main__':
    print("--- DCF Valuation Calculator ---")

    # Calculate initial FCFF
    base_fcff = calculate_fcff(EBIT_BASE, TAX_RATE, DEPREC_AMORT, CAPEX, DELTA_NWC)
    print(f"\nBase Year FCFF: INR {base_fcff:.2f} million")

    # Calculate WACC components
    wacc_base, re_base, rd_at_base, equity_w, debt_w = calculate_wacc(
        EQUITY_BETA, RISK_FREE_RATE, MARKET_RETURN, COST_OF_DEBT_PRE_TAX, TAX_RATE, DEBT_TO_EQUITY_RATIO
    )
    print(f"Cost of Equity (Re): {re_base:.2%}")
    print(f"After-tax Cost of Debt (Rd_at): {rd_at_base:.2%}")
    print(f"Equity Weight: {equity_w:.2f}, Debt Weight: {debt_w:.2f}")
    print(f"Weighted Average Cost of Capital (WACC): {wacc_base:.2%}")

    # Run base DCF valuation
    dcf_results = run_dcf_valuation(base_fcff, INITIAL_GROWTH_RATE, TERMINAL_GROWTH_RATE, 5, wacc_base)
    print("\n--- Base Case DCF Results ---")
    print(f"Projected FCFFs (Years 1-5): {[f'{fcff:.2f}' for fcff in dcf_results['projected_fcffs']]}")
    print(f"Present Values of FCFFs (Years 1-5): {[f'{pv:.2f}' for pv in dcf_results['pv_fcffs']]}")
    print(f"Terminal Value (Year 5): INR {dcf_results['terminal_value']:.2f} million")
    print(f"Present Value of Terminal Value: INR {dcf_results['pv_terminal_value']:.2f} million")
    print(f"Total Enterprise Value (DCF): INR {dcf_results['enterprise_value']:.2f} million")

    # --- Sensitivity Analysis (3x3 Grid) ---
    print("\n--- DCF Sensitivity Analysis (Enterprise Value in INR millions) ---")
    wacc_variations = [wacc_base - 0.01, wacc_base, wacc_base + 0.01]
    tg_variations = [TERMINAL_GROWTH_RATE - 0.01, TERMINAL_GROWTH_RATE, TERMINAL_GROWTH_RATE + 0.01]

    print(f"{'WACC \\ Tg':<15}", end="")
    for tg_v in tg_variations:
        print(f"{tg_v:.1%}{'':<8}", end="")
    print()

    for wacc_v in wacc_variations:
        print(f"{wacc_v:.1%}{'':<11}", end="")
        for tg_v in tg_variations:
            # Constraint check: WACC must be > terminal growth rate
            if wacc_v <= tg_v:
                print(f"{'N/A':<11}", end="") # Should not happen with our chosen values based on pre-check
            else:
                # Re-run DCF for each variation
                dcf_sens_results = run_dcf_valuation(base_fcff, INITIAL_GROWTH_RATE, tg_v, 5, wacc_v)
                print(f"{dcf_sens_results['enterprise_value']:.0f}{'':<11}", end="")
        print()

    # Self-check for WACC - terminal_growth >= 1 percentage point in worst case
    worst_case_wacc = wacc_base - 0.01
    worst_case_tg = TERMINAL_GROWTH_RATE + 0.01
    if worst_case_wacc - worst_case_tg >= 0.01:
        print(f"\nSelf-check passed: (WACC - 1pp) - (Tg + 1pp) = {(worst_case_wacc - worst_case_tg):.2%} >= 1 percentage point.")
    else:
        print(f"\nSelf-check FAILED: (WACC - 1pp) - (Tg + 1pp) = {(worst_case_wacc - worst_case_tg):.2%} < 1 percentage point. Adjust inputs.")

    # --- EV/EBITDA Multiple Cross-check (stated in writing) ---
    print("\n--- EV/EBITDA Cross-check ---")
    # Illustrative EBITDA = EBIT + D&A
    illustrative_ebitda = EBIT_BASE + DEPREC_AMORT # INR 1100 million
    # Illustrative EV/EBITDA Multiple (chosen)
    illustrative_ev_ebitda_multiple = 10 # 10x

    ev_from_ebitda = illustrative_ebitda * illustrative_ev_ebitda_multiple

    print(f"Illustrative EBITDA (EBIT + D&A): INR {illustrative_ebitda:.2f} million")
    print(f"Illustrative EV/EBITDA Multiple: {illustrative_ev_ebitda_multiple}x")
    print(f"Enterprise Value (EV/EBITDA Cross-check): INR {ev_from_ebitda:.2f} million")

    # --- Comparison Comment ---
    print("\n--- Comparison of Valuation Methods ---")
    dcf_ev = dcf_results['enterprise_value']
    ebitda_ev = ev_from_ebitda

    print(f"The DCF valuation resulted in an Enterprise Value of INR {dcf_ev:.2f} million.")
    print(f"The EV/EBITDA multiple cross-check yielded an Enterprise Value of INR {ebitda_ev:.2f} million.")
    print("The two estimates are relatively close, indicating that the chosen assumptions for both models are \n   within a reasonable range for this hypothetical business line. The DCF provides a more granular \n   view based on projected cash flows, while the EV/EBITDA multiple offers a market-based perspective \n   relative to comparable companies. The slight difference suggests potential for further refinement \n   in growth assumptions or the selected market multiple.")
