import pytest
from bs4 import BeautifulSoup
from quant_synthica_api.providers.screener_provider import ScreenerProvider

SAMPLE_HTML = """
<html>
<body>
  <h1>Reliance Industries Ltd</h1>
  <div class="about">Reliance is India's largest private company.</div>
  <ul id="top-ratios">
    <li><span class="name">Market Cap</span><span class="value">₹ 17,00,000 Cr.</span></li>
    <li><span class="name">Current Price</span><span class="value">₹ 1,250</span></li>
    <li><span class="name">Stock P/E</span><span class="value">24.5</span></li>
    <li><span class="name">ROCE</span><span class="value">12.5 %</span></li>
    <li><span class="name">ROE</span><span class="value">10.2 %</span></li>
  </ul>
  <section id="profit-loss">
    <table class="data-table">
      <thead>
        <tr><th></th><th>Mar 2023</th><th>Mar 2024</th></tr>
      </thead>
      <tbody>
        <tr><td>Sales +</td><td>1000</td><td>1200</td></tr>
        <tr><td>Net Profit</td><td>100</td><td>120</td></tr>
      </tbody>
    </table>
  </section>
</body>
</html>
"""

def test_screener_parsing_logic():
    provider = ScreenerProvider()
    soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
    
    top_ratios = provider._parse_top_ratios(soup)
    assert top_ratios["current_price"] == 1250.0
    assert top_ratios["pe_ratio"] == 24.5
    assert top_ratios["roce"] == 12.5
    assert top_ratios["roe"] == 10.2

    pl = provider._parse_table_section(soup, "profit-loss")
    assert pl is not None
    assert pl.periods == ["Mar 2023", "Mar 2024"]
    assert len(pl.rows) == 2
    assert pl.rows[0].metric == "Sales"
    assert pl.rows[0].values["Mar 2023"] == 1000.0
    assert pl.rows[0].values["Mar 2024"] == 1200.0
