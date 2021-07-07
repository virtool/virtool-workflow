FROM virtool/external-tools:0.2.0

RUN curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose

RUN pip install poetry pytest pytest-asyncio pytest-xdist \
                pytest-cov pytest-aiohttp 

WORKDIR install

WORKDIR test
ENV VT_DB_CONNECTION_STRING=http://localhost:9050

COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "pytest"]


