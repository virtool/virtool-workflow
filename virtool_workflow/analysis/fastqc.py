"""Utilities and fixtures for running FastQC."""

from __future__ import annotations

import asyncio
import shutil
import statistics
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Protocol, TextIO

from pyfixtures import fixture

from virtool_workflow import RunSubprocess
from virtool_workflow.analysis.utils import ReadPaths


@dataclass
class NucleotidePoint:
    g: float
    a: float
    t: float
    c: float


@dataclass
class QualityPoint:
    mean: float
    median: float
    lower_quartile: float
    upper_quartile: float
    tenth_percentile: float
    ninetieth_percentile: float


class BaseQualityParser:
    """Parse the section of FastQC output containing per-base quality data."""

    pattern = ">>Per base sequence quality"

    def __init__(self):
        self.data: list[QualityPoint] = []

    def composite(self, parser: BaseQualityParser):
        p = BaseQualityParser()

        p.data = [
            QualityPoint(
                mean=statistics.mean([this.mean, other.mean]),
                median=statistics.mean([this.median, other.median]),
                lower_quartile=statistics.mean(
                    [this.lower_quartile, other.lower_quartile],
                ),
                upper_quartile=statistics.mean(
                    [this.upper_quartile, other.upper_quartile],
                ),
                tenth_percentile=statistics.mean(
                    [this.tenth_percentile, other.tenth_percentile],
                ),
                ninetieth_percentile=statistics.mean(
                    [this.ninetieth_percentile, other.ninetieth_percentile],
                ),
            )
            for this, other in zip(self.data, parser.data)
        ]

        return p

    def handle(self, f: TextIO):
        max_index = -1

        while True:
            line = f.readline().rstrip()

            if line == ">>END_MODULE":
                break

            if not line or line[0] == "#":
                continue

            split = line.split()

            # Convert all fields except first to 2-decimal floats.
            try:
                values = [float(value) for value in split[1:]]
            except ValueError as err:
                if "NaN" not in str(err):
                    raise

                values = _handle_base_quality_nan(split)

            (
                mean,
                median,
                lower_quartile,
                upper_quartile,
                tenth_percentile,
                ninetieth_percentile,
            ) = values

            indexes = _calculate_index_range(split[0])

            for i in indexes:
                self.data.append(
                    QualityPoint(
                        mean=mean,
                        median=median,
                        lower_quartile=lower_quartile,
                        upper_quartile=upper_quartile,
                        tenth_percentile=tenth_percentile,
                        ninetieth_percentile=ninetieth_percentile,
                    ),
                )

                if i - max_index != 1:
                    raise ValueError("Non-contiguous index")

                max_index = i


class BasicStatisticsParser:
    """Parse the section of FastQC output containing basic statistics."""

    pattern = ">>Basic Statistics"

    def __init__(self):
        self.count = 0
        self.encoding = None
        self.gc = None
        self.length = None

        self._populated = False

    def composite(self, parser: BasicStatisticsParser):
        p = BasicStatisticsParser()

        p.count = self.count + parser.count
        p.encoding = self.encoding
        p.gc = (self.gc + parser.gc) / 2
        p.length = [
            min(self.length + parser.length),
            max(self.length + parser.length),
        ]

        return p

    def handle(self, f: IO):
        while True:
            line = f.readline().rstrip()

            if line.startswith("#"):
                continue

            if line == ">>END_MODULE":
                break

            if "Total Sequences" in line:
                self.count = int(line.split("\t")[1])

            elif "Encoding" in line:
                self.encoding = line.split("\t")[1]

            elif "Sequence length" in line:
                length_range = [int(s) for s in line.split("\t")[1].split("-")]
                self.length = [min(length_range), max(length_range)]

            # GC-content
            elif "%GC" in line and "#" not in line:
                self.gc = float(line.split("\t")[1])


class NucleotideCompositionParser:
    """Parse the section of FastQC output containing per-base nucleotide composition."""

    pattern = ">>Per base sequence content"

    def __init__(self):
        self.data: list[NucleotidePoint] = []

    def composite(self, parser: NucleotideCompositionParser):
        """Make a composite dataset given another :class:`.NucleotideCompositionParser`."""
        p = NucleotideCompositionParser()

        p.data = [
            NucleotidePoint(
                g=(this.g + other.g) / 2,
                a=(this.a + other.a) / 2,
                t=(this.t + other.t) / 2,
                c=(this.c + other.c) / 2,
            )
            for this, other in zip(self.data, parser.data)
        ]

        return p

    def handle(self, f: TextIO):
        max_index = -1

        while True:
            line = f.readline().rstrip()

            if line == ">>END_MODULE":
                break

            if not line or line[0] == "#":
                continue

            split = line.split()

            try:
                g, a, t, c = (float(value) for value in split[1:])
            except ValueError as err:
                if "NaN" not in str(err):
                    raise

                g, a, t, c = _handle_base_quality_nan(split)

            indexes = _calculate_index_range(split[0])

            for i in indexes:
                self.data.append(NucleotidePoint(g, a, t, c))

                if i - max_index != 1:
                    raise ValueError("Non-contiguous index")

                max_index = i


class SequenceQualityParser:
    """Parse the section of FastQC output containing per-sequence quality data."""

    pattern = ">>Per sequence quality scores"

    def __init__(self):
        self.data = [0] * 50

    def composite(self, parser: SequenceQualityParser):
        p = SequenceQualityParser()
        p.data = [sum(both) for both in zip(self.data, parser.data)]

        return p

    def handle(self, f: TextIO):
        while True:
            line = f.readline().rstrip()

            if not line or line.startswith("#"):
                continue

            if line == ">>END_MODULE":
                break

            line = line.split()

            quality = int(line[0])
            count = int(float(line[1]))

            self.data[quality] = count


@dataclass
class FastQCSide:
    base_quality: BaseQualityParser
    basic_statistics: BasicStatisticsParser
    nucleotide_composition: NucleotideCompositionParser
    sequence_quality: SequenceQualityParser


def _calculate_index_range(base: str) -> range:
    pos = [int(x) for x in base.split("-")]

    if len(pos) > 1:
        return range(pos[0] - 1, pos[1])

    return range(pos[0] - 1, pos[0])


def _handle_base_quality_nan(split_line: list) -> list:
    """Parse a per-base quality line from FastQC containing NaN values.

    :param split_line: the quality line split into a :class:`.List`
    :return: replacement values

    """
    values = split_line[1:]

    for value in values:
        try:
            return [value for _ in values]
        except ValueError:
            pass

    # Return all zeroes if none of the quality values are numbers.
    if set(values) == {"NaN"}:
        return [0] * 4

    joined = ",".join(split_line)

    raise ValueError(f"Could not parse base quality values '{joined}'")


def _parse_fastqc(fastqc_path: Path, output_path: Path) -> dict:
    """Parse the FastQC results at `fastqc_path`.

    All FastQC data except the textual data file are removed.

    :param fastqc_path: the FastQC output data path
    :param sample_path: the FastQC text output file will be moved here
    :return: a dict containing a representation of the parsed FastQC data

    """
    output_path.mkdir(exist_ok=True, parents=True)

    sides = []

    # Get the text data files from the FastQC output
    for path in fastqc_path.iterdir():
        if not path.is_dir():
            continue

        for file_path in path.iterdir():
            if file_path.name != "fastqc_data.txt":
                continue

            new_path = output_path / f"{path.name}.txt"

            shutil.move(file_path, new_path)

            base_quality = BaseQualityParser()
            basic_statistics = BasicStatisticsParser()
            nucleotide_composition = NucleotideCompositionParser()
            sequence_quality = SequenceQualityParser()

            with open(new_path) as f:
                while True:
                    line = f.readline()

                    if not line:
                        break

                    if basic_statistics.pattern in line:
                        basic_statistics.handle(f)

                    if base_quality.pattern in line:
                        base_quality.handle(f)

                    if nucleotide_composition.pattern in line:
                        nucleotide_composition.handle(f)

                    if SequenceQualityParser.pattern in line:
                        sequence_quality.handle(f)

            sides.append(
                FastQCSide(
                    base_quality=base_quality,
                    basic_statistics=basic_statistics,
                    nucleotide_composition=nucleotide_composition,
                    sequence_quality=sequence_quality,
                ),
            )

    if len(sides) == 1:
        left = sides[0]

        return {
            "bases": [
                [
                    round(n, 3)
                    for n in [
                        point.mean,
                        point.median,
                        point.lower_quartile,
                        point.upper_quartile,
                        point.tenth_percentile,
                        point.ninetieth_percentile,
                    ]
                ]
                for point in left.base_quality.data
            ],
            "composition": [
                [round(n, 1) for n in [point.g, point.a, point.t, point.c]]
                for point in left.nucleotide_composition.data
            ],
            "count": left.basic_statistics.count,
            "encoding": left.basic_statistics.encoding,
            "gc": left.basic_statistics.gc,
            "length": left.basic_statistics.length,
            "sequences": left.sequence_quality.data,
        }

    left, right = sides

    basic = left.basic_statistics.composite(right.basic_statistics)

    return {
        "bases": [
            [
                round(n, 3)
                for n in [
                    point.mean,
                    point.median,
                    point.lower_quartile,
                    point.upper_quartile,
                    point.tenth_percentile,
                    point.ninetieth_percentile,
                ]
            ]
            for point in left.base_quality.composite(right.base_quality).data
        ],
        "composition": [
            [round(n, 1) for n in [point.g, point.a, point.t, point.c]]
            for point in left.nucleotide_composition.composite(
                right.nucleotide_composition,
            ).data
        ],
        "count": basic.count,
        "length": basic.length,
        "encoding": left.basic_statistics.encoding,
        "gc": basic.gc,
        "sequences": left.sequence_quality.composite(right.sequence_quality).data,
    }


class FastQCRunner(Protocol):
    """A protocol describing callables that can be used to run FastQC."""

    async def __call__(self, paths: ReadPaths, output_path: Path) -> dict: ...


@fixture
async def fastqc(run_subprocess: RunSubprocess):
    """Provides an asynchronous function that can run FastQC as a subprocess.

    The function takes a one or two paths to FASTQ read files (:class:`.ReadPaths`) in
    a tuple.

    Example:
    -------
    .. code-block:: python

        @step
        async def step_one(fastqc: FastQCRunner, work_path: Path):
            fastqc_result = await fastqc((
                work_path / "reads_1.fq",
                work_path / "reads_2.fq"
            ))

    """
    temp_path = Path(await asyncio.to_thread(tempfile.mkdtemp))

    async def func(paths: ReadPaths, output_path: Path) -> dict:
        command = [
            "fastqc",
            "-f",
            "fastq",
            "-o",
            str(temp_path),
            "--extract",
            *[str(path) for path in paths],
        ]

        await run_subprocess(command)

        return _parse_fastqc(temp_path, output_path)

    return func
