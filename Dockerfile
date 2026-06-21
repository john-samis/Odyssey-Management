FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/odyssey_attendance ./src/odyssey_attendance

RUN python -m pip install --upgrade pip && python -m pip install .

ENTRYPOINT ["odyssey-attendance-report"]
