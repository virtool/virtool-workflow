"""
Fixture and class for representing the analysis associated with a workflow run.

"""

from pyfixtures import fixture

from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.data_model.analysis import WFAnalysis


@fixture
async def analysis(analysis_provider: AnalysisProvider) -> WFAnalysis:
    """
    A fixture that returns an :class:`.Analysis` object representing the analysis associated with the running workflow.

    :param analysis_provider: the analysis provider
    :return: the analysis object

    """

    async def upload_files(files):
        for path, fmt in files:
            await analysis_provider.upload(path, fmt)

    analysis_dict = (await analysis_provider.get()).dict()

    return WFAnalysis(**analysis_dict, upload_files=upload_files)
