from virtool_workflow.storage.paths import context_directory
from virtool_workflow.subtractions.subtraction import subtractions
from virtool_workflow.execute import run_in_executor, thread_pool_executor

mock_subtraction_base = dict(
    name="foobar",
    nickname="bar",
    count="7",
    gc={"A":0.2, "T":0.2, "C":0.2, "G":0.4}
)

mock_subtractions = {str(i):{**mock_subtraction_base, "id": str(i)} for i in range(5)}

subtraction_data_filenames = [
    "subtraction.fa.gz",
    "reference.1.bt2",
    "reference.3.bt2",
    "reference.2.bt2",
    "reference.4.bt2",
    "reference.rev.1.bt2",
    "reference.rev.2.bt2",
]


async def _fetch_subtraction_document(id: str):
    return mock_subtractions[id]


async def test_subtractions(monkeypatch):
    monkeypatch.setattr("virtool_workflow.db.db.fetch_subtraction_document", _fetch_subtraction_document)

    subtraction_id = mock_subtractions["0"]["id"]

    with context_directory(f"data/subtractions/{subtraction_id}") as current_subtraction_data_path:

        for name in subtraction_data_filenames:
            (current_subtraction_data_path/name).touch()

        with context_directory(f"temp/subtractions") as subtraction_path:

            _subtractions = await subtractions(
                job_args=dict(subtraction_id=subtraction_id),
                subtraction_data_path=current_subtraction_data_path.parent,
                subtraction_path=subtraction_path,
                run_in_executor=run_in_executor(thread_pool_executor())
            )

            print(_subtractions)
            raise




