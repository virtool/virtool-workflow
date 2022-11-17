FROM python:3.10-slim as pip
WORKDIR /install
RUN apt-get update && apt-get install -y build-essential curl python-dev
RUN curl -sSL https://install.python-poetry.org | python -
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
RUN /root/.local/bin/poetry export > requirements.txt
RUN pip install --user -r requirements.txt


FROM ghcr.io/virtool/workflow-tools:2.0.1
COPY --from=pip /root/.local /root/.local
WORKDIR /workflow
COPY virtool_workflow ./virtool_workflow
COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .
RUN ls .
RUN pip install --user .

ENTRYPOINT ["workflow", "run"]
