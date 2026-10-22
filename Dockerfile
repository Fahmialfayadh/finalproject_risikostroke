# ==============================================================
# Multi-Stage Build untuk Flask + Rust PyO3 Extension (stroke_calc)
# ==============================================================

# --------------------------------------------------------------
# Stage 1: Build Rust Extension menggunakan Maturin
# --------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependensi compiler dan Rust toolchain
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

# Install maturin untuk build Python wheel dari crate PyO3
RUN pip install --no-cache-dir maturin

# Salin source code crate Rust
COPY stroke_calc /build/stroke_calc
WORKDIR /build/stroke_calc

# Build wheel package biner (.whl) untuk Linux
RUN maturin build --release --out /build/wheels


# --------------------------------------------------------------
# Stage 2: Runtime Image (Ringan dan Bersih tanpa Rust Toolchain)
# --------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Atur environment variables Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Install dependensi sistem yang dibutuhkan pustaka Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Salin dan install modul stroke_calc (.whl) yang dihasilkan Stage 1
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Salin dan install dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pycryptodome

# Salin seluruh kode aplikasi ke dalam container
COPY . /app

# Pastikan folder instance database SQLite tersedia
RUN mkdir -p /app/instance

# Expose port aplikasi Flask
EXPOSE 5000

# Jalankan server menggunakan Gunicorn (WSGI HTTP Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

