FROM python:3.12.3-bookworm
WORKDIR /test
COPY --from=ghcr.io/virtool/workflow-tools:2.0.1 /opt/fastqc /opt/fastqc
COPY --from=ghcr.io/virtool/workflow-tools:2.0.1 /opt/hmmer /opt/hmmer
COPY --from=ghcr.io/virtool/workflow-tools:2.0.1 /usr/local/bin/pigz /usr/local/bin/
COPY --from=ghcr.io/virtool/workflow-tools:2.0.1 /usr/local/bin/skewer /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends default-jre
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin:/opt/hmmer/bin:/opt/fastqc"
COPY vendor/skewer /usr/local/bin/skewer
COPY poetry.lock pyproject.toml README.md ./
RUN poetry install --no-root
COPY example/ example/
COPY tests/ tests/
COPY virtool_workflow/ virtool_workflow/
RUN poetry install --only-root
COPY workflow.py .
