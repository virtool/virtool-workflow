FROM python:3.9-buster

RUN pip install poetry tox tox-docker

WORKDIR install

RUN wget https://github.com/BenLangmead/bowtie2/releases/download/v2.3.2/bowtie2-2.3.2-legacy-linux-x86_64.zip \
    && unzip bowtie2-2.3.2-legacy-linux-x86_64.zip \
    && cp bowtie2-2.3.2-legacy/bowtie2* /usr/local/bin

RUN wget http://eddylab.org/software/hmmer/hmmer-3.3.2.tar.gz \
    && tar -xvf hmmer-3.3.2.tar.gz \
    && cd hmmer-3.3.2 \
    && ./configure --prefix /install/hmmer \
    && make \
    && make install \
    && cd .. \
    && ln -s /install/hmmer/bin/hmm* /usr/local/bin

WORKDIR test
ENV VT_DB_CONNECTION_STRING=http://localhost:9050

COPY . .

ENTRYPOINT ["tox"]

