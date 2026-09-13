import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from quant_synthica_api.main import app
from quant_synthica_api.services.cache_service import cache

@pytest.fixture(autouse=True)
def clean_cache():
    cache.memory_fallback.clear()
    yield
    cache.memory_fallback.clear()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
