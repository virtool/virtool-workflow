FROM virtool/workflow-tools:1.0.0
WORKDIR /test

RUN pip install poetry

COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "pytest"]


