from typing import List, Optional
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.schemas.quant import (
    ReturnsMetrics, RiskMetrics, VolatilityMetrics, TechnicalIndicators, QuantSummaryData
)
from quant_synthica_api.quant.returns import calculate_returns
from quant_synthica_api.quant.risk import calculate_risk, calculate_volatility_metrics
from quant_synthica_api.quant.indicators import calculate_technical_indicators

class QuantEngine:
    @staticmethod
    def compute_returns(items: List[OHLCVItem], symbol: str) -> ReturnsMetrics:
        return calculate_returns(items, symbol)

    @staticmethod
    def compute_risk(items: List[OHLCVItem], symbol: str, risk_free_rate: float = 0.06) -> RiskMetrics:
        return calculate_risk(items, symbol, risk_free_rate=risk_free_rate)

    @staticmethod
    def compute_volatility(items: List[OHLCVItem], symbol: str) -> VolatilityMetrics:
        return calculate_volatility_metrics(items, symbol)

    @staticmethod
    def compute_technical(items: List[OHLCVItem], symbol: str) -> TechnicalIndicators:
        return calculate_technical_indicators(items, symbol)

    @staticmethod
    def compute_summary(items: List[OHLCVItem], symbol: str, risk_free_rate: float = 0.06) -> QuantSummaryData:
        returns = calculate_returns(items, symbol)
        risk = calculate_risk(items, symbol, risk_free_rate=risk_free_rate)
        technical = calculate_technical_indicators(items, symbol)
        return QuantSummaryData(
            symbol=symbol,
            returns=returns,
            risk=risk,
            technical=technical
        )
