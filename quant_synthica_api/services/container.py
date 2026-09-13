from quant_synthica_api.providers.yfinance_provider import YFinanceProvider
from quant_synthica_api.providers.screener_provider import ScreenerProvider
from quant_synthica_api.providers.tradingview_provider import TradingViewProvider
from quant_synthica_api.services.fallback_service import FallbackService
from quant_synthica_api.services.market_service import MarketService
from quant_synthica_api.services.fundamentals_service import FundamentalsService
from quant_synthica_api.services.screener_service import ScreenerService
from quant_synthica_api.services.quant_service import QuantService
from quant_synthica_api.services.stock_profile_service import StockProfileService
from quant_synthica_api.services.valuation_service import ValuationService
from quant_synthica_api.services.portfolio_service import PortfolioService
from quant_synthica_api.services.sentiment_service import SentimentService
from quant_synthica_api.services.report_service import ReportService

class ServiceContainer:
    def __init__(self):
        # Providers
        self.yf_provider = YFinanceProvider()
        self.screener_provider = ScreenerProvider()
        self.tv_provider = TradingViewProvider()

        # Fallback Service
        self.fallback_service = FallbackService(
            yf_provider=self.yf_provider,
            screener_provider=self.screener_provider,
            tv_provider=self.tv_provider
        )

        # Core Services
        self.market_service = MarketService(
            yf_provider=self.yf_provider,
            fallback_service=self.fallback_service
        )
        self.fundamentals_service = FundamentalsService(
            screener_provider=self.screener_provider,
            yf_provider=self.yf_provider,
            fallback_service=self.fallback_service
        )
        self.screener_service = ScreenerService(
            tv_provider=self.tv_provider
        )
        self.quant_service = QuantService(
            yf_provider=self.yf_provider
        )
        self.stock_profile_service = StockProfileService(
            market_service=self.market_service,
            fundamentals_service=self.fundamentals_service,
            quant_service=self.quant_service
        )
        self.valuation_service = ValuationService(
            fundamentals_service=self.fundamentals_service,
            market_service=self.market_service
        )
        self.portfolio_service = PortfolioService(
            market_service=self.market_service
        )
        self.sentiment_service = SentimentService(
            market_service=self.market_service
        )
        self.report_service = ReportService(
            market_service=self.market_service,
            fundamentals_service=self.fundamentals_service,
            valuation_service=self.valuation_service
        )

# Global container singleton
container = ServiceContainer()

def get_market_service() -> MarketService:
    return container.market_service

def get_fundamentals_service() -> FundamentalsService:
    return container.fundamentals_service

def get_screener_service() -> ScreenerService:
    return container.screener_service

def get_quant_service() -> QuantService:
    return container.quant_service

def get_stock_profile_service() -> StockProfileService:
    return container.stock_profile_service

def get_valuation_service() -> ValuationService:
    return container.valuation_service

def get_portfolio_service() -> PortfolioService:
    return container.portfolio_service

def get_sentiment_service() -> SentimentService:
    return container.sentiment_service

def get_report_service() -> ReportService:
    return container.report_service

