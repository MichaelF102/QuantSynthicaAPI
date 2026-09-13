import re
import time
from typing import Optional, Dict, Any, List, Tuple
import requests
from bs4 import BeautifulSoup

from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger
from quant_synthica_api.providers.base import BaseProvider, ProviderResult
from quant_synthica_api.schemas.fundamentals import (
    FinancialStatementData, FinancialRow, RatiosData, ShareholdingItem,
    ShareholdingResponse, UnifiedFundamentalsData, PeersResponse, PeerItem,
    CorporateAnalysisResponse, DocumentsResponse, DocumentItem
)
from quant_synthica_api.utils.rate_limiter import SyncThrottle

settings = get_settings()

class ScreenerProvider(BaseProvider):
    BASE_URL = "https://www.screener.in/company/{symbol}/"
    CONSOLIDATED_URL = "https://www.screener.in/company/{symbol}/consolidated/"

    def __init__(self):
        super().__init__(name="screener")
        self.throttle = SyncThrottle(min_interval=settings.SCREENER_MIN_INTERVAL)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self._raw_cache: Dict[str, Tuple[float, BeautifulSoup]] = {}
        self._cache_ttl = 300.0  # 5 minutes in-memory cache

    def health_check(self) -> bool:
        try:
            res = self.session.get("https://www.screener.in", timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def _fetch_soup(self, symbol: str) -> Optional[BeautifulSoup]:
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        now = time.monotonic()
        if clean_sym in self._raw_cache:
            ts, cached_soup = self._raw_cache[clean_sym]
            if now - ts < self._cache_ttl:
                return cached_soup

        self.throttle.acquire()
        urls_to_try = [
            self.CONSOLIDATED_URL.format(symbol=clean_sym),
            self.BASE_URL.format(symbol=clean_sym),
        ]

        for url in urls_to_try:
            for attempt in range(3):
                try:
                    resp = self.session.get(url, timeout=10)
                    if resp.status_code == 200 and len(resp.text) > 2000:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        self._raw_cache[clean_sym] = (now, soup)
                        return soup
                    elif resp.status_code == 404:
                        break
                    elif resp.status_code == 429:
                        time.sleep(2.0 * (attempt + 1))
                except requests.RequestException as e:
                    logger.warning(f"Screener request error for {clean_sym} ({url}): {e}")
                    time.sleep(1.0 * (attempt + 1))
        
        return None

    def _parse_top_ratios(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
        ratios: Dict[str, Optional[float]] = {}
        ul = soup.find("ul", id="top-ratios")
        if not ul:
            return ratios

        for li in ul.find_all("li"):
            name_el = li.find(class_="name")
            val_el = li.find(class_="nowrap value") or li.find(class_="value")
            if name_el and val_el:
                key = name_el.text.strip().lower()
                val_text = val_el.text.strip().replace("₹", "").replace(",", "").replace("%", "").strip()
                if "/" in val_text:
                    parts = val_text.split("/")
                    try:
                        ratios["high_52w"] = float(parts[0].strip().replace(",", ""))
                        ratios["low_52w"] = float(parts[1].strip().replace(",", ""))
                    except (ValueError, IndexError):
                        pass
                else:
                    try:
                        first_num = re.search(r"[-+]?\d*\.?\d+", val_text)
                        if first_num:
                            val_num = float(first_num.group())
                            if "market cap" in key:
                                ratios["market_cap_cr"] = val_num
                                ratios["market_cap"] = val_num * 1e7
                            elif "current price" in key:
                                ratios["current_price"] = val_num
                            elif "stock p/e" in key or "p/e" in key:
                                ratios["pe_ratio"] = val_num
                            elif "book value" in key:
                                ratios["book_value"] = val_num
                            elif "dividend yield" in key:
                                ratios["dividend_yield"] = val_num
                            elif "roce" in key:
                                ratios["roce"] = val_num
                            elif "roe" in key:
                                ratios["roe"] = val_num
                            elif "face value" in key:
                                ratios["face_value"] = val_num
                    except ValueError:
                        pass
        return ratios

    def _parse_table_section(self, soup: BeautifulSoup, section_id: str) -> Optional[FinancialStatementData]:
        sec = soup.find("section", id=section_id)
        if not sec:
            return None
        tbl = sec.find("table", class_="data-table")
        if not tbl:
            return None

        thead = tbl.find("thead")
        raw_headers = [th.text.strip() for th in thead.find_all("th")] if thead else []
        headers = [h for h in raw_headers if h and h != "+"]
        
        tbody = tbl.find("tbody")
        rows: List[FinancialRow] = []
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all(["td", "th"])
                if not tds:
                    continue
                row_name = re.sub(r"\s*\+\s*", "", tds[0].text.strip()).strip()
                if not row_name or row_name == "Raw PDF":
                    continue
                val_tds = tds[1:]
                vals_dict: Dict[str, Optional[float]] = {}
                for i, col_name in enumerate(headers):
                    if i < len(val_tds):
                        txt = val_tds[i].text.strip().replace(",", "").replace("%", "")
                        try:
                            vals_dict[col_name] = float(txt) if txt and txt != "-" else None
                        except ValueError:
                            vals_dict[col_name] = None
                    else:
                        vals_dict[col_name] = None
                rows.append(FinancialRow(metric=row_name, values=vals_dict))

        return FinancialStatementData(statement_type=section_id, periods=headers, rows=rows)

    def _parse_shareholding(self, soup: BeautifulSoup) -> Tuple[List[str], List[ShareholdingItem]]:
        sec = soup.find("section", id="shareholding")
        if not sec:
            return [], []
        tbl = sec.find("table", class_="data-table")
        if not tbl:
            return [], []

        thead = tbl.find("thead")
        headers = [th.text.strip() for th in thead.find_all("th") if th.text.strip()] if thead else []
        categories: List[ShareholdingItem] = []

        tbody = tbl.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all(["td", "th"])
                if not tds:
                    continue
                cat_name = re.sub(r"\s*\+\s*", "", tds[0].text.strip()).strip()
                if not cat_name:
                    continue
                val_dict: Dict[str, Optional[float]] = {}
                for i, col_name in enumerate(headers):
                    if (i + 1) < len(tds):
                        val_txt = tds[i + 1].text.strip().replace("%", "").replace(",", "")
                        try:
                            val_dict[col_name] = float(val_txt) if val_txt and val_txt != "-" else None
                        except ValueError:
                            val_dict[col_name] = None
                categories.append(ShareholdingItem(holder_category=cat_name, values=val_dict))

        return headers, categories

    def get_company_profile(self, symbol: str) -> ProviderResult[UnifiedFundamentalsData]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(
                data=None, provider=self.name, success=False, error=f"Company '{clean_sym}' not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000
            )

        name_el = soup.find("h1")
        name = name_el.text.strip() if name_el else clean_sym

        about_el = soup.find("div", class_="about")
        about = about_el.text.strip() if about_el else None

        top_ratios = self._parse_top_ratios(soup)
        pb = None
        if top_ratios.get("current_price") and top_ratios.get("book_value"):
            try:
                pb = round(top_ratios["current_price"] / top_ratios["book_value"], 2)
            except ZeroDivisionError:
                pass

        ratios_data = RatiosData(
            pe_ratio=top_ratios.get("pe_ratio"),
            pb_ratio=pb,
            roe=top_ratios.get("roe"),
            roce=top_ratios.get("roce"),
            dividend_yield=top_ratios.get("dividend_yield"),
            book_value=top_ratios.get("book_value"),
            market_cap=top_ratios.get("market_cap"),
            current_price=top_ratios.get("current_price"),
            high_52w=top_ratios.get("high_52w"),
            low_52w=top_ratios.get("low_52w"),
            face_value=top_ratios.get("face_value"),
        )

        quarters = self._parse_table_section(soup, "quarters")
        profit_loss = self._parse_table_section(soup, "profit-loss")
        balance_sheet = self._parse_table_section(soup, "balance-sheet")
        cash_flow = self._parse_table_section(soup, "cash-flow")
        sh_periods, sh_items = self._parse_shareholding(soup)

        data = UnifiedFundamentalsData(
            symbol=clean_sym,
            name=name,
            about=about,
            ratios=ratios_data,
            quarterly_results=quarters,
            profit_and_loss=profit_loss,
            balance_sheet=balance_sheet,
            cash_flow=cash_flow,
            shareholding=sh_items if sh_items else None
        )

        return ProviderResult(data=data, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    def get_statement(self, symbol: str, statement_type: str) -> ProviderResult[FinancialStatementData]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        section_map = {
            "income-statement": "profit-loss",
            "profit-loss": "profit-loss",
            "quarters": "quarters",
            "quarterly": "quarters",
            "balance-sheet": "balance-sheet",
            "cash-flow": "cash-flow",
            "ratios": "ratios"
        }
        sec_id = section_map.get(statement_type, statement_type)
        stmt = self._parse_table_section(soup, sec_id)
        if not stmt:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Statement {statement_type} not found for {clean_sym}", latency_ms=(time.monotonic() - t0) * 1000)

        return ProviderResult(data=stmt, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    def get_ratios(self, symbol: str) -> ProviderResult[RatiosData]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        top_ratios = self._parse_top_ratios(soup)
        pb = None
        if top_ratios.get("current_price") and top_ratios.get("book_value"):
            try:
                pb = round(top_ratios["current_price"] / top_ratios["book_value"], 2)
            except ZeroDivisionError:
                pass

        ratios_sec = self._parse_table_section(soup, "ratios")
        hist_dict: Dict[str, Dict[str, Optional[float]]] = {}
        if ratios_sec and ratios_sec.rows:
            for r in ratios_sec.rows:
                hist_dict[r.metric] = r.values

        ratios_data = RatiosData(
            pe_ratio=top_ratios.get("pe_ratio"),
            pb_ratio=pb,
            roe=top_ratios.get("roe"),
            roce=top_ratios.get("roce"),
            dividend_yield=top_ratios.get("dividend_yield"),
            book_value=top_ratios.get("book_value"),
            market_cap=top_ratios.get("market_cap"),
            current_price=top_ratios.get("current_price"),
            high_52w=top_ratios.get("high_52w"),
            low_52w=top_ratios.get("low_52w"),
            face_value=top_ratios.get("face_value"),
            historical_ratios=hist_dict if hist_dict else None
        )
        return ProviderResult(data=ratios_data, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    def get_shareholding(self, symbol: str) -> ProviderResult[ShareholdingResponse]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        periods, categories = self._parse_shareholding(soup)
        resp = ShareholdingResponse(
            symbol=clean_sym,
            periods=periods,
            categories=categories,
            metadata={
                "source": self.name,
                "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cached": False,
                "latency_ms": (time.monotonic() - t0) * 1000
            }
        )
        return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    # --- Extended Screener.in Features ---

    def get_peers(self, symbol: str) -> ProviderResult[PeersResponse]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        sec = soup.find("section", id="peers")
        sector_name = None
        peers: List[PeerItem] = []
        if sec:
            sub = sec.find("p", class_="sub")
            if sub:
                sector_name = sub.text.strip().replace("Sector:", "").strip()

            tbl = sec.find("table", class_="data-table")
            if not tbl:
                # Fetch via warehouse-id endpoint
                card = soup.find(attrs={"data-warehouse-id": True})
                if card:
                    wid = card.get("data-warehouse-id")
                    try:
                        p_resp = self.session.get(f"https://www.screener.in/api/company/{wid}/peers/", timeout=5)
                        if p_resp.status_code == 200:
                            p_soup = BeautifulSoup(p_resp.text, "html.parser")
                            tbl = p_soup.find("table")
                    except Exception as e:
                        logger.warning(f"Failed to fetch peers API: {e}")

            if tbl and tbl.find("tbody"):
                for tr in tbl.find("tbody").find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) >= 4:
                        name = tds[1].text.strip()
                        def _get_f(idx):
                            if idx < len(tds):
                                try:
                                    txt = tds[idx].text.strip().replace(",", "").replace("%", "")
                                    return float(txt) if txt and txt != "-" else None
                                except ValueError:
                                    return None
                            return None

                        peers.append(PeerItem(
                            name=name,
                            price=_get_f(2),
                            pe=_get_f(3),
                            market_cap=_get_f(4),
                            dividend_yield=_get_f(5),
                            net_profit_quarter=_get_f(6),
                            qtr_profit_var=_get_f(7),
                            sales_quarter=_get_f(8),
                            qtr_sales_var=_get_f(9),
                            roce=_get_f(10)
                        ))


        resp = PeersResponse(
            symbol=clean_sym,
            sector=sector_name,
            peers=peers,
            metadata={
                "source": self.name,
                "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cached": False,
                "latency_ms": (time.monotonic() - t0) * 1000
            }
        )
        return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    def get_analysis(self, symbol: str) -> ProviderResult[CorporateAnalysisResponse]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        pros: List[str] = []
        cons: List[str] = []
        sec = soup.find("section", id="analysis")
        if sec:
            pros_div = sec.find(class_="pros")
            if pros_div:
                pros = [li.text.strip() for li in pros_div.find_all("li") if li.text.strip()]
            cons_div = sec.find(class_="cons")
            if cons_div:
                cons = [li.text.strip() for li in cons_div.find_all("li") if li.text.strip()]

        resp = CorporateAnalysisResponse(
            symbol=clean_sym,
            pros=pros,
            cons=cons,
            metadata={
                "source": self.name,
                "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cached": False,
                "latency_ms": (time.monotonic() - t0) * 1000
            }
        )
        return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

    def get_documents(self, symbol: str, limit: int = 20) -> ProviderResult[DocumentsResponse]:
        t0 = time.monotonic()
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        soup = self._fetch_soup(clean_sym)
        if not soup:
            return ProviderResult(data=None, provider=self.name, success=False, error=f"Symbol {clean_sym} not found on Screener.in", latency_ms=(time.monotonic() - t0) * 1000)

        docs: List[DocumentItem] = []
        sec = soup.find("section", id="documents")
        if sec:
            for a in sec.find_all("a", href=True):
                text = a.text.strip()
                href = a["href"]
                if not text or text == "All" or not href.startswith("http"):
                    continue

                doc_type = "announcement"
                text_lower = text.lower()
                if "concall" in text_lower or "transcript" in text_lower:
                    doc_type = "concall"
                elif "annual report" in text_lower:
                    doc_type = "annual_report"
                elif "presentation" in text_lower or "investor" in text_lower:
                    doc_type = "presentation"

                docs.append(DocumentItem(
                    title=text,
                    type=doc_type,
                    url=href
                ))
                if len(docs) >= limit:
                    break

        resp = DocumentsResponse(
            symbol=clean_sym,
            count=len(docs),
            documents=docs,
            metadata={
                "source": self.name,
                "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cached": False,
                "latency_ms": (time.monotonic() - t0) * 1000
            }
        )
        return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
