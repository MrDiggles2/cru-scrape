FROM python:3.11-buster AS build

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install

FROM python:3.11-slim-buster

RUN apt-get update && apt-get install libpq5 -y

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src ./src
COPY data ./data
COPY README.md ./

ENTRYPOINT ["python", "-m", "src.main" ]
