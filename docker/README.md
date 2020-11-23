t # The Virtool Workflow Base Image

## Containerizing Standalone Workflows

```dockerfile
FROM virtool_workflow_standalone

COPY my_workflow.py workflow.py
COPY my_fixtures.py fixtures.py
```

The `virtool_workflow_standalone` Dockerfile sets the ENTRYPOINT command to;
```
workflow run
```

As such any CLI arguments (see `workflow run --help`) can be passed along when
running the container. 

## Install Additional Dependencies Using Multi-stage Builds

Docker's [multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build/) allow you to build a 
piece of software in one image and copy it's binaries to your desired image. 

For example here is how you would install `fastqc` into the `virtool_workflow_standalone` image.

```dockerfile
FROM alpine:latest as fastqc

WORKDIR /build
RUN wget https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.5.zip && \
    unzip fastqc_v0.11.5.zip

FROM virtool_workflow_standalone

COPY --from=fastqc build/FastQC /opt/fastqc

COPY my_workflow.py workflow.py
```

