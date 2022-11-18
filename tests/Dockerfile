FROM virtool/workflow-tools:2.0.1
WORKDIR /test
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install --no-root
COPY . .
ENTRYPOINT ["poetry", "run", "pytest"]
