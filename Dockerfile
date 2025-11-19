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
RUN chmod +x ./docker-entrypoint.sh

EXPOSE ${APP_PORT:-8000}

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["--workers", "1"]
