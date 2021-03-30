FROM virtool/workflow:0.0.0

COPY ./workflow ./workflow

ENTRYPOINT ["workflow", "run", "-f workflow/__init__.py", "test_job"]

