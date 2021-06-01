from pathlib import Path
from typing import List

import virtool_workflow
from virtool_workflow.data_model.subtractions import (NucleotideComposition,
                                                      Subtraction)


@virtool_workflow.step
def test_correct_subtractions(
        subtractions: List[Subtraction],
        work_path: Path
):

    sub1, sub2 = subtractions

    assert sub1.id == "no3nlhgn"
    assert sub2.id == "f6698qcc"

    assert sub1.gc == NucleotideComposition(
        a=0.25, t=0.25, g=0.25, c=0.25, n=0.0
    )
    assert sub1.name == sub2.name == "subtraction_1"

    assert sub1.path == work_path / "subtractions" / sub1.id
    assert sub2.path == work_path / "subtractions" / sub2.id

    for name in (
        "subtraction.fa.gz",
        "subtraction.1.bt2",
        "subtraction.2.bt2",
        "subtraction.3.bt2",
        "subtraction.4.bt2",
        "subtraction.rev.1.bt2",
        "subtraction.rev.2.bt2",
    ):
        assert (sub1.path/name).exists()
        assert (sub2.path/name).exists()
