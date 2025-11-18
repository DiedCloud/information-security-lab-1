FROM python:3.13
LABEL authors="DiedCloud"

WORKDIR /app

# Install poetry
RUN pip install --upgrade pip
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /app/

# Install dependencies
RUN poetry config virtualenvs.create false
RUN poetry cache clear pypi --all && poetry install --no-root --only main
RUN rm -rf $POETRY_CACHE_DIR

COPY . .

EXPOSE ${APP_PORT}

ENV RUNNING_IN_DOCKER=true

CMD ["--workers", "1"]

ENTRYPOINT ["gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${APP_PORT}"]
