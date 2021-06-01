import json
from virtool_workflow import step
from virtool_workflow.analysis.analysis import Analysis
from virtool_workflow.api.analysis import AnalysisProvider
from pathlib import Path
from virtool_workflow.hooks import on_finish


@step
def fetch_analysis(analysis: Analysis, work_path: Path):
    test_file = work_path/"test.json"

    test_file.write_text(json.dumps({"TEST": 0}))

    analysis.upload(test_file, "json")


@on_finish
async def check_file_uploded(analysis_provider: AnalysisProvider, logger):
    analysis = await analysis_provider
    assert len(analysis.files) == 1
