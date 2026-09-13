#!/usr/bin/env bash
set -e

# Run QuantSynthica API locally using venv
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

if [ -f "./venv/bin/uvicorn" ]; then
    ./venv/bin/uvicorn quant_synthica_api.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn quant_synthica_api.main:app --host 0.0.0.0 --port 8000 --reload
fi
