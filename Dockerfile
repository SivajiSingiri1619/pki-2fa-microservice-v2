# ---------- STAGE 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (cache optimization)
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- STAGE 2: Runtime ----------
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copy Python deps from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ /app/app/

# Copy keys (required inside container)
COPY student_private.pem student_private.pem
COPY student_public.pem student_public.pem
COPY instructor_public.pem instructor_public.pem

# Create volume directories
RUN mkdir -p /data /cron

COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY scripts/ /app/scripts/

RUN chmod 0644 /etc/cron.d/2fa-cron \
    && mkdir -p /cron \
    && chmod 777 /cron



# Expose API port
EXPOSE 8080

# Start FastAPI (cron added in next step)
CMD ["sh", "-c", "while true; do python3 /app/scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1; sleep 60; done & uvicorn app.main:app --host 0.0.0.0 --port 8080"]



