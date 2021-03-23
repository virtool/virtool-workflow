FROM virtool/external-tools:0.2.0

RUN pip install poetry pytest pytest-asyncio pytest-xdist pytest-cov pytest-aiohttp

WORKDIR install

WORKDIR test
ENV VT_DB_CONNECTION_STRING=http://localhost:9050

COPY ./pyproject.toml .
RUN poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "pytest"]


