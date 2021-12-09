FROM virtool/workflow-tools:1.0.0
WORKDIR /test

COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "pytest"]


