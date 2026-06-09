FROM python:3.13-slim

# Dependencias de sistema para Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
    libdrm2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2t64 libxshmfence1 \
    fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Instalar dependencias Python
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Instalar Chromium para Playwright
RUN uv run playwright install chromium

# Copiar código
COPY api/ api/
COPY WebScrappers_Eps/ WebScrappers_Eps/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
