FROM ghcr.io/virtool/workflow-tools:2.0.1
WORKDIR /test
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install
ENTRYPOINT ["pytest"]
