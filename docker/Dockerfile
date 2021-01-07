# Bowtie2
FROM alpine:latest as bowtie
WORKDIR /build
RUN wget https://github.com/BenLangmead/bowtie2/releases/download/v2.3.2/bowtie2-2.3.2-legacy-linux-x86_64.zip && \
    unzip bowtie2-2.3.2-legacy-linux-x86_64.zip && \
    mkdir bowtie2 && \
    cp bowtie2-2.3.2-legacy/bowtie2* bowtie2

FROM python:3.9 as pip_install
ARG VIRTOOL_WORKFLOW_PIP_PACKAGE="virtool-workflow==0.1.0"
RUN pip install --user $VIRTOOL_WORKFLOW_PIP_PACKAGE

FROM python:3.9-slim as main
COPY --from=pip_install /root/.local /root/.local
COPY --from=bowtie /build/bowtie2/* /usr/local/bin/
ENV PATH $PATH:/root/.local/bin
ENTRYPOINT ["workflow", "run"]


