FROM python:3.9 as pip_install

ARG VIRTOOL_WORKFLOW_PIP_PACKAGE="virtool-workflow==0.1.0"
RUN pip install --user $VIRTOOL_WORKFLOW_PIP_PACKAGE

FROM python:3.9-slim as main

COPY --from=pip_install /root/.local /root/.local
ENV PATH $PATH:/root/.local/bin
ENTRYPOINT ["workflow", "run"]


