import asyncio

from _pytest._py.path import LocalPath
from aioredis import Redis

from virtool_workflow.pytest_plugin.data import Data
from virtool_workflow.runtime.run_subprocess import watch_pipe


async def test_cmd(
    data: Data,
    jobs_api_connection_string: str,
    redis: Redis,
    redis_connection_string: str,
    tmp_path: LocalPath,
):
    data.job.args.update(
        {
            "files": [
                {
                    "id": 1,
                    "name": "reads_1.fq.gz",
                    "size": 100,
                },
                {
                    "id": 2,
                    "name": "reads_2.fq.gz",
                    "size": 100,
                },
            ],
            "sample_id": data.new_sample.id,
        }
    )

    await redis.rpush("job_test", "test_job")

    p = await asyncio.create_subprocess_exec(
        "poetry",
        "run",
        "run-workflow",
        "--jobs-api-connection-string",
        jobs_api_connection_string,
        "--redis-connection-string",
        redis_connection_string,
        "--redis-list-name",
        "job_test",
        "--work-path",
        str(tmp_path),
        limit=1024 * 1024 * 128,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    async def handler(line):
        print(line.decode().rstrip())

    g = asyncio.gather(
        watch_pipe(p.stderr, handler),
        watch_pipe(p.stdout, handler),
    )

    await p.wait()
    await p.communicate()
    await g
