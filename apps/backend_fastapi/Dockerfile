# syntax=docker/dockerfile:1.6
# ──────────────────────────────────────────────────────────────────────────────
# MediSign FastAPI backend — multi-stage Docker build
#
# Stage 1 (builder): install Python dependencies into a clean prefix that we
#                    later copy into the runtime image. Keeps the final image
#                    small (no compilers, no pip cache).
# Stage 2 (runtime): minimal runtime layer that runs as a non-root user and
#                    starts uvicorn with multiple workers behind --proxy-headers.
# ──────────────────────────────────────────────────────────────────────────────

# ─── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Build deps for psycopg/Pillow/opencv. Removed from runtime stage.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend_fastapi/pyproject.toml ./
COPY apps/backend_fastapi/README.md ./

# Install dependencies into a virtualenv that we copy into the final image.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install .

# Copy the rest of the source code and install the project itself.
COPY apps/backend_fastapi/ ./
RUN /opt/venv/bin/pip install --no-deps .


# ─── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

# Runtime libraries only — no compilers.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libgl1 \
        libglib2.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1001 medisign \
    && useradd --uid 1001 --gid 1001 --create-home --shell /usr/sbin/nologin medisign

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=medisign:medisign apps/backend_fastapi/ /app/

USER medisign

EXPOSE 8000

# Configurable worker count — defaults to 2. Override with -e WEB_CONCURRENCY=N.
ENV WEB_CONCURRENCY=2

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

# `--proxy-headers` lets uvicorn honour X-Forwarded-* set by an upstream proxy.
# `--forwarded-allow-ips=*` is acceptable here because the container is meant
# to run behind a trusted ingress controller; tighten this when you know the
# IP range of your ingress.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY} --proxy-headers --forwarded-allow-ips=*"]
