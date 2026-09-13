FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and local repositories if present
COPY quant_synthica_api/ /app/quant_synthica_api/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/
COPY .env.example /app/.env
COPY yfinance* /app/yfinance/
COPY TradingView-Screener* /app/TradingView-Screener/

# Ensure upstream providers exist on cloud builds if not copied
RUN if [ ! -d "/app/yfinance/yfinance" ]; then git clone https://github.com/ranaroussi/yfinance.git /app/yfinance; fi && \
    if [ ! -d "/app/TradingView-Screener/src" ]; then git clone https://github.com/shner-elmo/TradingView-Screener.git /app/TradingView-Screener; fi


EXPOSE 8000

CMD ["sh", "-c", "uvicorn quant_synthica_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
