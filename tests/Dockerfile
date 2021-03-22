FROM virtool/external-tools:0.2.0

RUN pip install poetry tox tox-docker

WORKDIR install

WORKDIR test
ENV VT_DB_CONNECTION_STRING=http://localhost:9050

COPY . .

ENTRYPOINT ["tox"]

