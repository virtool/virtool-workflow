# virtool-workflow dependencies
FROM python:3.8-slim as pip_install
WORKDIR /install
RUN pip install --user poetry==1.1.6
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
RUN /root/.local/bin/poetry export > requirements.txt
RUN pip install --user -r requirements.txt


FROM virtool/workflow-tools:1.0.0
COPY --from=pip_install /root/.local /root/.local

WORKDIR /workflow
COPY . .
RUN pip install --user .

ENTRYPOINT ["workflow", "run"]
