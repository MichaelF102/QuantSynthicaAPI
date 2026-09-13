"""Reports and institutional factsheet exports resource."""

from typing import Optional
from quantsynthica.resources.base import BaseResource


class ReportsResource(BaseResource):
    def download_excel(self, symbol: str, output_path: Optional[str] = None) -> bytes:
        """Download multi-tab Excel financial workbook (.xlsx) for a symbol."""
        content = self._request("GET", f"reports/excel/{symbol}", raw_response=True)
        if output_path:
            with open(output_path, "wb") as f:
                f.write(content)
        return content

    def get_tearsheet_html(self, symbol: str) -> str:
        """Get institutional HTML factsheet / tearsheet."""
        content = self._request("GET", f"reports/tearsheet/{symbol}", raw_response=True)
        return content.decode("utf-8") if isinstance(content, bytes) else str(content)
