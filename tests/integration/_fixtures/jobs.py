import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase


@pytest.fixture
def job_id(request):
    """A unique job_id for each integration test"""
    return f"vt_integration_{request.node.originalname}"



@pytest.fixture
async def test_user(db: AsyncIOMotorDatabase):
    users = db.get_collection("users")

    user = {
        "_id": "test_admin",
        "id": "test_admin",
        "administrator": True,
        "handle": False,
    }

    await users.insert_one(user)

    return user


@pytest.fixture
def create_job(db: AsyncIOMotorDatabase, job_id: str, test_user, request):
    """Create a mock job document."""
    jobs = db.get_collection("jobs")

    async def _create_job(args: dict):
        job = {
            "_id": job_id,
            "args": args,
            "status": [
                {
                    "state": "waiting",
                    "stage": None,
                    "error": None,
                    "progress": 0,
                    "timestamp": None
                }

            ],
            "user": test_user,
            "acquired": False,
            "workflow": request.node.originalname
        }
        await jobs.insert_one(job)

        return job

    return _create_job


