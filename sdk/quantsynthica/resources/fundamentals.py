"""Fundamentals resource for balance sheets, P&L, cash flow, ratios, peers, shareholding."""

from quantsynthica.resources.base import BaseResource, DotDict


class FundamentalsResource(BaseResource):
    def get_unified(self, symbol: str) -> DotDict:
        """Get unified 360-degree fundamental metrics."""
        return self._request("GET", f"fundamentals/{symbol}")

    def get_income_statement(self, symbol: str) -> DotDict:
        """Get annual/quarterly income statement / P&L."""
        return self._request("GET", f"fundamentals/{symbol}/income-statement")

    def get_balance_sheet(self, symbol: str) -> DotDict:
        """Get balance sheet statement."""
        return self._request("GET", f"fundamentals/{symbol}/balance-sheet")

    def get_cash_flow(self, symbol: str) -> DotDict:
        """Get cash flow statement."""
        return self._request("GET", f"fundamentals/{symbol}/cash-flow")

    def get_ratios(self, symbol: str) -> DotDict:
        """Get key valuation & profitability ratios."""
        return self._request("GET", f"fundamentals/{symbol}/ratios")

    def get_shareholding(self, symbol: str) -> DotDict:
        """Get shareholding pattern across promoter, FII, DII, and public."""
        return self._request("GET", f"fundamentals/{symbol}/shareholding")

    def get_institutional_holders(self, symbol: str) -> DotDict:
        """Get top institutional shareholders."""
        return self._request("GET", f"fundamentals/{symbol}/institutional-holders")

    def get_mutual_funds(self, symbol: str) -> DotDict:
        """Get mutual fund shareholders."""
        return self._request("GET", f"fundamentals/{symbol}/mutual-funds")

    def get_insider_transactions(self, symbol: str) -> DotDict:
        """Get insider trades."""
        return self._request("GET", f"fundamentals/{symbol}/insider-transactions")

    def get_sustainability(self, symbol: str) -> DotDict:
        """Get ESG risk ratings."""
        return self._request("GET", f"fundamentals/{symbol}/sustainability")

    def get_peers(self, symbol: str) -> DotDict:
        """Get industry peer comparison table."""
        return self._request("GET", f"fundamentals/{symbol}/peers")

    def get_analysis(self, symbol: str) -> DotDict:
        """Get pros and cons corporate analysis."""
        return self._request("GET", f"fundamentals/{symbol}/analysis")

    def get_documents(self, symbol: str) -> DotDict:
        """Get concall transcripts and annual reports."""
        return self._request("GET", f"fundamentals/{symbol}/documents")
