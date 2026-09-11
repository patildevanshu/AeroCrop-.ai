# ── Stage 1: Build React Frontend ──────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python Backend Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runner

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU (supports both x86_64 and ARM64 / aarch64 architectures)
RUN pip install --no-cache-dir \
    torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, model, frontend build, and application code
COPY backend/ ./backend/
COPY model/ ./model/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY main.py config.py ./
RUN mkdir -p /app/data /app/uploads

# Environment defaults (optimized for multi-core ARM64/x86 VPS)
ENV HOST=0.0.0.0 \
    PORT=3000 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    DATABASE_URL="sqlite+aiosqlite:///data/aerocrop.db"

EXPOSE 3000 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-3000}/api/health || exit 1

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-3000}"]
