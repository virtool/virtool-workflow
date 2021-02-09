import docker

from virtool_workflow_runtime.hooks import on_load_config, on_docker_connect


@on_load_config
async def create_docker_client(docker_daemon_url, scope):
    if not docker_daemon_url:
        scope["docker"] = docker.from_env()
    else:
        scope["docker"] = docker.DockerClient(base_url=docker_daemon_url)

    scope["docker"].ping()

    await on_docker_connect.trigger(scope)
