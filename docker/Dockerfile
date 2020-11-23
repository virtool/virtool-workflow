FROM python:3.9 as build_wheel

ARG VIRTOOL_WORKFLOW_PIP_PACKAGE="virtool-workflow==0.1.0"

WORKDIR /build
RUN pip install --user $VIRTOOL_WORKFLOW_PIP_PACKAGE

FROM python:3.9-slim as main

COPY --from=build_wheel /root/.local /root/.local

ENV PATH $PATH:/root/.local/bin
ENTRYPOINT ["workflow", "run"]


