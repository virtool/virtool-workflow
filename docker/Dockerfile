FROM python:3.9 as build_wheel

ARG VIRTOOL_CORE_REPO_URL="https://github.com/virtool/virtool-core"
ARG VIRTOOL_WORKFLOW_REPO_URL="https://github.com/virtool/virtool-workflow"

WORKDIR /build
RUN git clone $VIRTOOL_CORE_REPO_URL \
    && cd virtool-core \
    && python setup.py bdist_wheel \
    && pip install --user dist/*.whl # installs to .local

RUN git clone $VIRTOOL_WORKFLOW_REPO_URL \
    && cd virtool-workflow \
    && python setup.py bdist_wheel \
    && pip install --user dist/*.whl # installs to .local

FROM python:3.9-slim as main

COPY --from=build_wheel /root/.local /root/.local

ENV PATH $PATH:/root/.local/bin
ENTRYPOINT ["workflow", "run"]


