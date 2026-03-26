FROM python:3.11-slim

# Install system libs needed by asyncpg, lxml, Pillow, etc.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment — lives at /app/.venv which is backed by a
# named volume in dev so it survives source-code bind-mount overrides.
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies as a separate cached layer; only re-runs when
# requirements.txt changes (or on rebuild).
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source (overridden by bind-mount in dev).
COPY . .

EXPOSE 8000
