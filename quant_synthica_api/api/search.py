from fastapi import APIRouter, Query
from quant_synthica_api.services.symbol_resolver import SymbolResolver, KNOWN_MAPPINGS
from typing import List, Dict, Any

router = APIRouter(tags=["Search"])

@router.get("/search", summary="Search and resolve stock symbols")
def search_symbols(q: str = Query(..., min_length=1, description="Symbol or query text")):
    query = q.strip().upper()
    results = []
    
    # Check known mappings
    for sym, details in KNOWN_MAPPINGS.items():
        if query in sym or query in details.get("name", "").upper() or query == details.get("bse"):
            r = SymbolResolver.resolve(sym)
            results.append(r.model_dump())

    # If no matches, attempt resolution
    if not results:
        try:
            r = SymbolResolver.resolve(query)
            results.append(r.model_dump())
        except Exception:
            pass

    return {
        "query": q,
        "count": len(results),
        "results": results
    }
