# syntax=docker/dockerfile:1

# ---- Base stage: shared configuration ----
FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./

# ---- Builder stage: install dependencies into a virtualenv ----
FROM base AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ---- Test stage: run the test suite against the built environment ----
FROM builder AS test

COPY . .

RUN python -m pytest && touch /tmp/tests-passed

# ---- Runtime stage: minimal image used to actually run the app ----
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy the pre-built virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Depend on the test stage so building the runtime image always requires the
# test suite to have passed first (the marker file itself is not used).
COPY --from=test /tmp/tests-passed /tmp/tests-passed

# Copy only the application source needed at runtime
COPY src ./src

# Run as a non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
