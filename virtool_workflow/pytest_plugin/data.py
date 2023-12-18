import datetime
from dataclasses import dataclass
from pathlib import Path

import pytest
from pydantic_factories import ModelFactory, Use
from virtool_core.models.analysis import Analysis
from virtool_core.models.index import Index, IndexNested
from virtool_core.models.job import JobAcquired, JobMinimal, JobPing
from virtool_core.models.ml import MLModelRelease
from virtool_core.models.reference import Reference
from virtool_core.models.samples import (
    Sample,
    SampleNested,
)
from virtool_core.models.subtraction import (
    Subtraction,
    SubtractionNested,
    SubtractionFile,
)

from virtool_workflow.pytest_plugin.utils import SUBTRACTION_FILENAMES


@dataclass
class Data:
    analysis: Analysis
    """An analysis being populated in the active workflow."""

    index: Index
    """A finalized index to be used for testing analyses."""

    new_index: Index
    """An un-finalized index for testing index creation workflows."""

    job: JobAcquired
    """A fake job."""

    ml: MLModelRelease | None
    """An ML model release used in the active analysis."""

    reference: Reference
    """A reference to be used for testing analyses and index creation workflows."""

    sample: Sample
    """A finalized sample to be used for testing analyses."""

    new_sample: Sample
    """An un-finalized sample for testing sample creation workflows."""

    subtraction: Subtraction
    """A finalized subtraction to be used for testing analyses."""

    new_subtraction: Subtraction
    """An un-finalized subtraction for testing subtraction creation workflows."""


@pytest.fixture
def data(example_path: Path, static_datetime: datetime.datetime) -> Data:
    class AnalysisFactory(ModelFactory):
        __model__ = Analysis

        created_at = Use(lambda: static_datetime)
        updated_at = Use(lambda: static_datetime)

    class IndexFactory(ModelFactory[Index]):
        __model__ = Index

        created_at = Use(lambda: static_datetime)

    IndexFactory.seed_random(12)

    class JobFactory(ModelFactory):
        __model__ = JobAcquired

        created_at = Use(lambda: static_datetime)
        timestamp = Use(lambda: static_datetime)

    JobFactory.seed_random(55)

    class MLFactory(ModelFactory):
        __model__ = MLModelRelease

        created_at = Use(lambda: static_datetime)
        published_at = Use(lambda: static_datetime)

    class ReferenceFactory(ModelFactory):
        __model__ = Reference

        created_at = Use(lambda: static_datetime)

    ReferenceFactory.seed_random(22)

    class SampleFactory(ModelFactory):
        __model__ = Sample

        created_at = Use(lambda: static_datetime)
        removed_at = None
        uploaded_at = Use(lambda: static_datetime)

    SampleFactory.seed_random(5)

    class SubtractionFactory(ModelFactory):
        __model__ = Subtraction

        created_at = Use(lambda: static_datetime)

    job: JobAcquired = JobFactory.build()

    job.args = {
        "item_id": 1211,
        "resource_id": "foo",
        "test": True,
    }
    job.ping = JobPing(pinged_at=static_datetime)
    job.rights = {}

    """A finalized sample to be used for testing analyses."""
    sample = SampleFactory.build()
    sample.job = JobMinimal.parse_obj(job)
    sample.artifacts = []

    # A new sample with the fake job configured as the creation job for the sample.
    new_sample = SampleFactory.build()

    new_sample_job = JobFactory.build()
    new_sample_job.args["files"] = [
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
    ]
    new_sample_job.args["sample_id"] = new_sample.id

    new_sample.artifacts = []
    new_sample.job = JobMinimal.parse_obj(new_sample_job)
    new_sample.quality = None
    new_sample.reads = []
    new_sample.ready = False

    reference = ReferenceFactory.build()
    reference.targets = []

    index = IndexFactory.build()
    index.reference = Reference.parse_obj(reference)
    index.ready = True

    new_index: Index = IndexFactory.build()
    new_index.reference = Reference.parse_obj(reference)
    new_index.files = []
    new_index.ready = False

    ml: MLModelRelease = MLFactory.build()
    ml.ready = True
    ml.model.id = 5
    ml.id = 231

    subtraction = SubtractionFactory.build()
    subtraction.files = [
        SubtractionFile(
            download_url=f"/subtractions/{subtraction.id}/files/{filename}",
            id=(i + 1),
            name=filename,
            size=(example_path / "subtraction" / filename).stat().st_size,
            subtraction=subtraction.id,
            type="bowtie2",
        )
        for i, filename in enumerate(SUBTRACTION_FILENAMES)
    ]

    new_subtraction = SubtractionFactory.build()
    new_subtraction.files = []
    new_subtraction.ready = False

    analysis: Analysis = AnalysisFactory.build()
    analysis.sample = SampleNested.parse_obj(sample)
    analysis.workflow = "pathoscope_bowtie"
    analysis.index = IndexNested.parse_obj(index)
    analysis.reference = Reference.parse_obj(reference)
    analysis.subtractions = [SubtractionNested.parse_obj(subtraction)]

    return Data(
        analysis=analysis,
        index=index,
        new_index=new_index,
        job=job,
        ml=ml,
        reference=reference,
        sample=sample,
        new_sample=new_sample,
        subtraction=subtraction,
        new_subtraction=new_subtraction,
    )
