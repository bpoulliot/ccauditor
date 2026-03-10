# ---------- Base Image ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# ---------- Dependencies Layer ----------
FROM base AS deps

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ---------- Dev Tools Layer ----------
FROM deps AS dev

RUN pip install --no-cache-dir \
    ruff \
    black \
    isort \
    pytest \
    pip-audit \
    pip-tools \
    pre-commit


# ---------- Runtime Image ----------
FROM base AS runtime

# Copy installed Python packages
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source
COPY app /app/app
COPY scripts /app/scripts
COPY requirements.txt /app

EXPOSE 8501
EXPOSE 8000

RUN chmod +x /app/scripts/start_app.sh

CMD ["/app/scripts/start_app.sh"]