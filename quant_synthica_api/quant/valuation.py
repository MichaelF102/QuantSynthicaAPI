"""Valuation models for fundamental and quantitative analysis.

Implements:
- Discounted Cash Flow (DCF) with Gordon Growth & Exit Multiple.
- Piotroski F-Score (9-point fundamental financial strength score).
- Altman Z-Score (bankruptcy and financial distress predictor).
- Benjamin Graham Number & Net-Net valuation.
"""

from typing import Dict, Any, List, Optional
import math


def calculate_dcf(
    free_cash_flow: float,
    growth_rate: float,
    discount_rate: float,
    terminal_growth_rate: float = 0.03,
    years: int = 5,
    net_debt: float = 0.0,
    shares_outstanding: float = 1.0,
    current_price: Optional[float] = None,
    exit_multiple: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate Discounted Cash Flow (DCF) valuation.

    Args:
        free_cash_flow: Starting Free Cash Flow (most recent annual).
        growth_rate: Expected annual FCF growth rate for projection period (e.g. 0.12 for 12%).
        discount_rate: WACC or required discount rate (e.g. 0.10 for 10%).
        terminal_growth_rate: Perpetual terminal growth rate (default 0.03 for 3%).
        years: Projection period in years (default 5).
        net_debt: Total Debt minus Cash and Equivalents.
        shares_outstanding: Number of diluted shares outstanding.
        current_price: Current market price per share (optional for margin of safety).
        exit_multiple: Optional EV/EBITDA or EV/FCF exit multiple for terminal value.

    Returns:
        Dictionary containing projected cash flows, enterprise value, equity value,
        fair value per share, and margin of safety.
    """
    if discount_rate <= terminal_growth_rate and exit_multiple is None:
        # Prevent division by zero or negative denominator in Gordon Growth
        discount_rate = terminal_growth_rate + 0.01

    if shares_outstanding <= 0:
        shares_outstanding = 1.0

    projected_fcf: List[Dict[str, Any]] = []
    pv_projected_fcf = 0.0
    current_fcf = free_cash_flow

    for year in range(1, years + 1):
        current_fcf = current_fcf * (1.0 + growth_rate)
        discount_factor = 1.0 / ((1.0 + discount_rate) ** year)
        pv = current_fcf * discount_factor
        pv_projected_fcf += pv
        projected_fcf.append({
            "year": year,
            "projected_fcf": round(current_fcf, 2),
            "discount_factor": round(discount_factor, 4),
            "present_value": round(pv, 2),
        })

    final_year_fcf = current_fcf

    # Terminal Value
    if exit_multiple is not None and exit_multiple > 0:
        terminal_value = final_year_fcf * exit_multiple
        tv_method = f"Exit Multiple ({exit_multiple:.1f}x)"
    else:
        terminal_value = (final_year_fcf * (1.0 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        tv_method = f"Gordon Growth ({terminal_growth_rate * 100:.1f}%)"

    pv_terminal_value = terminal_value / ((1.0 + discount_rate) ** years)
    enterprise_value = pv_projected_fcf + pv_terminal_value
    equity_value = enterprise_value - net_debt
    fair_value_per_share = max(0.0, equity_value / shares_outstanding)

    margin_of_safety_pct = None
    undervalued = None
    if current_price and current_price > 0:
        margin_of_safety_pct = round(((fair_value_per_share - current_price) / fair_value_per_share) * 100, 2) if fair_value_per_share > 0 else -100.0
        undervalued = fair_value_per_share > current_price

    return {
        "starting_fcf": round(free_cash_flow, 2),
        "assumptions": {
            "projection_years": years,
            "growth_rate_pct": round(growth_rate * 100, 2),
            "discount_rate_wacc_pct": round(discount_rate * 100, 2),
            "terminal_growth_rate_pct": round(terminal_growth_rate * 100, 2),
            "terminal_method": tv_method,
            "net_debt": round(net_debt, 2),
            "shares_outstanding": round(shares_outstanding, 2),
        },
        "projections": projected_fcf,
        "pv_of_cash_flows": round(pv_projected_fcf, 2),
        "terminal_value": round(terminal_value, 2),
        "pv_of_terminal_value": round(pv_terminal_value, 2),
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "fair_value_per_share": round(fair_value_per_share, 2),
        "current_price": round(current_price, 2) if current_price else None,
        "margin_of_safety_pct": margin_of_safety_pct,
        "is_undervalued": undervalued,
    }


def calculate_piotroski_f_score(
    net_income_curr: float,
    net_income_prev: float,
    cfo_curr: float,
    roa_curr: float,
    roa_prev: float,
    long_term_debt_curr: float,
    long_term_debt_prev: float,
    current_ratio_curr: float,
    current_ratio_prev: float,
    shares_curr: float,
    shares_prev: float,
    gross_margin_curr: float,
    gross_margin_prev: float,
    asset_turnover_curr: float,
    asset_turnover_prev: float,
) -> Dict[str, Any]:
    """Calculate the 9-point Piotroski F-Score.

    Returns:
        Dictionary with score (0 to 9), criteria breakdown, and strength rating.
    """
    criteria: Dict[str, Dict[str, Any]] = {}

    # Category 1: Profitability (4 points)
    criteria["positive_roa"] = {
        "name": "Positive Return on Assets",
        "category": "Profitability",
        "passed": roa_curr > 0,
        "value": round(roa_curr, 4),
        "point": 1 if roa_curr > 0 else 0,
    }
    criteria["positive_cfo"] = {
        "name": "Positive Operating Cash Flow",
        "category": "Profitability",
        "passed": cfo_curr > 0,
        "value": round(cfo_curr, 2),
        "point": 1 if cfo_curr > 0 else 0,
    }
    criteria["higher_roa"] = {
        "name": "Higher ROA vs Prior Year",
        "category": "Profitability",
        "passed": roa_curr > roa_prev,
        "delta": round(roa_curr - roa_prev, 4),
        "point": 1 if roa_curr > roa_prev else 0,
    }
    criteria["cash_flow_accrual"] = {
        "name": "CFO greater than Net Income (Accruals Quality)",
        "category": "Profitability",
        "passed": cfo_curr > net_income_curr,
        "delta": round(cfo_curr - net_income_curr, 2),
        "point": 1 if cfo_curr > net_income_curr else 0,
    }

    # Category 2: Leverage, Liquidity & Source of Funds (3 points)
    criteria["lower_leverage"] = {
        "name": "Lower Long-Term Debt / Leverage vs Prior Year",
        "category": "Leverage & Liquidity",
        "passed": long_term_debt_curr <= long_term_debt_prev,
        "delta": round(long_term_debt_curr - long_term_debt_prev, 2),
        "point": 1 if long_term_debt_curr <= long_term_debt_prev else 0,
    }
    criteria["higher_current_ratio"] = {
        "name": "Higher Current Ratio vs Prior Year",
        "category": "Leverage & Liquidity",
        "passed": current_ratio_curr >= current_ratio_prev,
        "delta": round(current_ratio_curr - current_ratio_prev, 4),
        "point": 1 if current_ratio_curr >= current_ratio_prev else 0,
    }
    criteria["no_dilution"] = {
        "name": "No Share Dilution (Shares <= Prior Year)",
        "category": "Leverage & Liquidity",
        "passed": shares_curr <= shares_prev * 1.005,  # allowing 0.5% buffer for small rounding
        "delta": round(shares_curr - shares_prev, 2),
        "point": 1 if shares_curr <= shares_prev * 1.005 else 0,
    }

    # Category 3: Operating Efficiency (2 points)
    criteria["higher_gross_margin"] = {
        "name": "Higher Gross Margin vs Prior Year",
        "category": "Operating Efficiency",
        "passed": gross_margin_curr > gross_margin_prev,
        "delta": round(gross_margin_curr - gross_margin_prev, 4),
        "point": 1 if gross_margin_curr > gross_margin_prev else 0,
    }
    criteria["higher_asset_turnover"] = {
        "name": "Higher Asset Turnover vs Prior Year",
        "category": "Operating Efficiency",
        "passed": asset_turnover_curr > asset_turnover_prev,
        "delta": round(asset_turnover_curr - asset_turnover_prev, 4),
        "point": 1 if asset_turnover_curr > asset_turnover_prev else 0,
    }

    total_score = sum(item["point"] for item in criteria.values())

    if total_score >= 8:
        strength = "Very Strong"
    elif total_score >= 6:
        strength = "Strong"
    elif total_score >= 4:
        strength = "Moderate"
    else:
        strength = "Weak / Financially Stressed"

    return {
        "f_score": total_score,
        "max_score": 9,
        "rating": strength,
        "profitability_score": sum(c["point"] for c in criteria.values() if c["category"] == "Profitability"),
        "leverage_liquidity_score": sum(c["point"] for c in criteria.values() if c["category"] == "Leverage & Liquidity"),
        "operating_efficiency_score": sum(c["point"] for c in criteria.values() if c["category"] == "Operating Efficiency"),
        "criteria": criteria,
    }


def calculate_altman_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    sales: float,
    is_manufacturing: bool = True,
) -> Dict[str, Any]:
    """Calculate the Altman Z-Score for financial distress and bankruptcy prediction.

    Original model (manufacturing):
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5

    Non-manufacturing model:
    Z' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    """
    if total_assets <= 0:
        total_assets = 1.0
    if total_liabilities <= 0:
        total_liabilities = 1.0

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = sales / total_assets

    if is_manufacturing:
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        if z_score >= 2.99:
            zone = "Safe Zone"
            probability_of_bankruptcy = "Low (< 10%)"
        elif z_score >= 1.81:
            zone = "Grey Zone"
            probability_of_bankruptcy = "Moderate (10% - 30%)"
        else:
            zone = "Distress Zone"
            probability_of_bankruptcy = "High (> 50%)"
    else:
        # Altman Z"-Score for service/non-manufacturing firms
        z_score = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
        if z_score >= 2.60:
            zone = "Safe Zone"
            probability_of_bankruptcy = "Low (< 10%)"
        elif z_score >= 1.10:
            zone = "Grey Zone"
            probability_of_bankruptcy = "Moderate (10% - 30%)"
        else:
            zone = "Distress Zone"
            probability_of_bankruptcy = "High (> 50%)"

    return {
        "z_score": round(z_score, 2),
        "zone": zone,
        "bankruptcy_risk": probability_of_bankruptcy,
        "model": "Manufacturing" if is_manufacturing else "Non-Manufacturing",
        "components": {
            "x1_working_capital_to_assets": round(x1, 4),
            "x2_retained_earnings_to_assets": round(x2, 4),
            "x3_ebit_to_assets": round(x3, 4),
            "x4_market_equity_to_liabilities": round(x4, 4),
            "x5_sales_to_assets": round(x5, 4) if is_manufacturing else None,
        },
    }


def calculate_graham_valuation(
    eps: float,
    book_value_per_share: float,
    current_price: Optional[float] = None,
    current_assets: Optional[float] = None,
    total_liabilities: Optional[float] = None,
    shares_outstanding: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate Benjamin Graham Number and Net-Net Working Capital valuation.

    Graham Number = sqrt(22.5 * EPS * BVPS)
    Net-Net Working Capital = Current Assets - Total Liabilities
    """
    graham_number = None
    if eps > 0 and book_value_per_share > 0:
        graham_number = round(math.sqrt(22.5 * eps * book_value_per_share), 2)

    margin_of_safety_pct = None
    if graham_number and current_price and current_price > 0:
        margin_of_safety_pct = round(((graham_number - current_price) / graham_number) * 100, 2)

    # Net-Net Working Capital (NCAV)
    ncav_per_share = None
    net_net_discount_pct = None
    if current_assets is not None and total_liabilities is not None and shares_outstanding and shares_outstanding > 0:
        ncav = current_assets - total_liabilities
        ncav_per_share = round(ncav / shares_outstanding, 2)
        if current_price and current_price > 0 and ncav_per_share > 0:
            net_net_discount_pct = round(((ncav_per_share - current_price) / ncav_per_share) * 100, 2)

    return {
        "graham_number": graham_number,
        "eps": round(eps, 2),
        "book_value_per_share": round(book_value_per_share, 2),
        "current_price": round(current_price, 2) if current_price else None,
        "graham_margin_of_safety_pct": margin_of_safety_pct,
        "is_undervalued_graham": (graham_number > current_price) if (graham_number and current_price) else None,
        "net_current_asset_value_per_share": ncav_per_share,
        "net_net_discount_pct": net_net_discount_pct,
    }
