"""Valuation models engine (DCF, Piotroski, Altman Z, Graham)."""

import math
from typing import Dict, Any, List, Optional
from quantsynthica.resources.base import DotDict


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
) -> DotDict:
    if discount_rate <= terminal_growth_rate and exit_multiple is None:
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
            "present_value": round(pv, 2),
        })

    final_year_fcf = current_fcf

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

    return DotDict({
        "starting_fcf": round(free_cash_flow, 2),
        "fair_value_per_share": round(fair_value_per_share, 2),
        "current_price": round(current_price, 2) if current_price else None,
        "margin_of_safety_pct": margin_of_safety_pct,
        "is_undervalued": undervalued,
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "terminal_value": round(terminal_value, 2),
        "assumptions": {
            "projection_years": years,
            "growth_rate_pct": round(growth_rate * 100, 2),
            "discount_rate_pct": round(discount_rate * 100, 2),
            "terminal_method": tv_method,
        },
        "projections": projected_fcf,
    })


def calculate_piotroski(
    roa: float = 0.12,
    cfo: float = 1000.0,
    net_income: float = 800.0,
    debt_decreased: bool = True,
    current_ratio_increased: bool = True,
    no_dilution: bool = True,
    gross_margin_increased: bool = True,
    asset_turnover_increased: bool = True,
) -> DotDict:
    points = {
        "positive_roa": roa > 0,
        "positive_cfo": cfo > 0,
        "cfo_greater_than_net_income": cfo > net_income,
        "lower_debt": debt_decreased,
        "higher_current_ratio": current_ratio_increased,
        "no_dilution": no_dilution,
        "higher_gross_margin": gross_margin_increased,
        "higher_asset_turnover": asset_turnover_increased,
    }
    score = sum(1 for v in points.values() if v)
    if score >= 7:
        rating = "Very Strong"
    elif score >= 5:
        rating = "Moderate"
    else:
        rating = "Weak"

    return DotDict({
        "f_score": score,
        "max_score": 9,
        "rating": rating,
        "criteria": points,
    })


def calculate_altman_z(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    sales: float,
) -> DotDict:
    if total_assets <= 0:
        total_assets = 1.0
    if total_liabilities <= 0:
        total_liabilities = 1.0

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = sales / total_assets

    z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
    if z_score >= 2.99:
        zone = "Safe Zone"
        risk = "Low (< 10%)"
    elif z_score >= 1.81:
        zone = "Grey Zone"
        risk = "Moderate (10% - 30%)"
    else:
        zone = "Distress Zone"
        risk = "High (> 50%)"

    return DotDict({
        "z_score": round(z_score, 2),
        "zone": zone,
        "bankruptcy_risk": risk,
    })


def calculate_graham(eps: float, bvps: float, current_price: Optional[float] = None) -> DotDict:
    gn = None
    if eps > 0 and bvps > 0:
        gn = round(math.sqrt(22.5 * eps * bvps), 2)

    mos = None
    undervalued = None
    if gn and current_price and current_price > 0:
        mos = round(((gn - current_price) / gn) * 100, 2)
        undervalued = gn > current_price

    return DotDict({
        "graham_number": gn,
        "eps": round(eps, 2),
        "book_value_per_share": round(bvps, 2),
        "current_price": round(current_price, 2) if current_price else None,
        "margin_of_safety_pct": mos,
        "is_undervalued": undervalued,
    })
