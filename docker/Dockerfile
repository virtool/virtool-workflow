# HMMER and Skewer
FROM debian:buster as debian
WORKDIR /build
RUN apt-get update && apt-get install -y build-essential wget bioperl
RUN wget https://bitbucket.org/wenchen_aafc/aodp_v2.0_release/raw/5fcd5d2dfde61cd87ad3c63b8c92babd281fc0dc/aodp-2.5.0.1.tar.gz && \
    tar -xvf aodp-2.5.0.1.tar.gz && \
    cd aodp-2.5.0.1 && \
    ./configure && \
    make && \
    mv b/aodp /build && \
    wget http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz && \
    tar -xf hmmer-3.2.1.tar.gz && \
    cd hmmer-3.2.1 && \
    ./configure --prefix /build/hmmer && \
    make && \
    make install && \
    wget https://github.com/relipmoc/skewer/archive/0.2.2.tar.gz && \
    tar -xf 0.2.2.tar.gz && \
    cd skewer-0.2.2 && \
    make && \
    mv skewer /build

# Bowtie2
FROM alpine:latest as bowtie
WORKDIR /build
RUN wget https://github.com/BenLangmead/bowtie2/releases/download/v2.3.2/bowtie2-2.3.2-legacy-linux-x86_64.zip && \
    unzip bowtie2-2.3.2-legacy-linux-x86_64.zip && \
    mkdir bowtie2 && \
    cp bowtie2-2.3.2-legacy/bowtie2* bowtie2

# FastQC
FROM alpine:latest as fastqc
WORKDIR /build
RUN wget https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.5.zip && \
    unzip fastqc_v0.11.5.zip

FROM python:3.9 as pip_install
ARG VIRTOOL_WORKFLOW_PIP_PACKAGE="virtool-workflow==0.4.0"
RUN pip install --user $VIRTOOL_WORKFLOW_PIP_PACKAGE

FROM python:3.9-slim as main
COPY --from=pip_install /root/.local /root/.local
COPY --from=bowtie /build/bowtie2/* /usr/local/bin/
COPY --from=debian /build/hmmer /opt/hmmer
COPY --from=debian /build/skewer /usr/local/bin/
COPY --from=fastqc /build/FastQC /opt/fastqc
ENV PATH $PATH:/root/.local/bin

RUN apt-get install -y pigz
ENTRYPOINT ["workflow", "run"]


