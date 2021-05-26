import logging
from typing import List
from pathlib import Path

import virtool_workflow
from virtool_workflow.data_model.hmms import HMM


@virtool_workflow.step
def ensure_hmmpress_executed(
        hmms: List[HMM],
        work_path: Path,
        logger: logging.Logger,
        results: dict
):
    for path in (
        work_path/"hmms/annotations.json",
        work_path/"hmms/profiles.hmm.h3m",
        work_path/"hmms/profiles.hmm.h3p",
        work_path/"hmms/profiles.hmm",
        work_path/"hmms/profiles.hmm.h3i",
        work_path/"hmms/annotations.json.gz",
        work_path/"hmms/profiles.hmm.h3f",
    ):
        assert path.exists()
        logger.info(f"{path} exists")

    results["complete"] = True
