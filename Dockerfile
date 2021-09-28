FROM python:3.8-buster as builder
WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

FROM builder
WORKDIR /app
CMD ["python", "main.py"]