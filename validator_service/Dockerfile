FROM python:3.11-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py main.py ./

ENV PORT=5005 \
    PYTHONUNBUFFERED=1

EXPOSE 5005

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5005/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5005"]
