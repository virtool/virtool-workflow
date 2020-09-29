# Base Image

A base image for Virtool workflows based on [continuumio/miniconda3](https://hub.docker.com/r/continuumio/miniconda3). 


- Pip, Conda, and Apt available
- bioconda already added as a channel
- virtool_core library installed
- virtool_workflow_sdk installed


## Usage

```dockerfile
FROM virtool_workflow:latest

# Install additional dependencies using pip, conda, apt
...

ENTRYPOINT ["python", "main.py"]
```