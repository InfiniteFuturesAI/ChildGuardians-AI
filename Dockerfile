# =============================================================================
# CHILD GUARDIANS - Production Dockerfile
# =============================================================================
# Multi-stage build for minimal attack surface
# Final image: ~150MB with no build tools
# =============================================================================

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY pyproject.toml README.md LICENSE ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Stage 2: Production Image
FROM python:3.12-slim as production

# Security: Create non-root user
RUN groupadd --gid 1000 childguardians && \
    useradd --uid 1000 --gid 1000 --shell /bin/false childguardians

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ src/

# Security: Set ownership
RUN chown -R childguardians:childguardians /app

# Security: Run as non-root user
USER childguardians

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Run with uvicorn
CMD ["uvicorn", "child_guardians.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
