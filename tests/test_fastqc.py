import shutil
import textwrap
from io import StringIO
from pathlib import Path

from syrupy import SnapshotAssertion

from virtool_workflow import RunSubprocess
from virtool_workflow.analysis.fastqc import (
    fastqc,
    BasicStatisticsParser,
    BaseQualityParser,
    NucleotideCompositionParser,
    SequenceQualityParser,
)


class TestBaseQualityParser:
    def test_ok(self, snapshot: SnapshotAssertion):
        """Test that the base quality parser works as expected."""
        s = StringIO(
            textwrap.dedent(
                """
                #Base	Mean	Median	Lower Quartile	Upper Quartile	10th Percentile	90th Percentile
                1	33.45152	34.0	34.0	34.0	34.0	34.0
                2	33.751	34.0	34.0	34.0	34.0	34.0
                3	33.8779	34.0	34.0	34.0	34.0	34.0
                4	33.85192	34.0	34.0	34.0	34.0	34.0
                5	33.78398	34.0	34.0	34.0	34.0	34.0
                6	37.63014	38.0	38.0	38.0	37.0	38.0
                7	37.54666	38.0	38.0	38.0	37.0	38.0
                8	37.38808	38.0	38.0	38.0	37.0	38.0
                9	37.4646	38.0	38.0	38.0	37.0	38.0
                10-14	37.521139999999995	38.0	38.0	38.0	36.8	38.0
                15-19	37.257456000000005	38.0	38.0	38.0	36.4	38.0
                20-24	37.51578000000001	38.0	38.0	38.0	37.0	38.0
                25-29	37.425292	38.0	38.0	38.0	37.0	38.0
                30-34	37.165183999999996	38.0	37.8	38.0	36.4	38.0
                >>END_MODULE
                """
            )
        )

        p = BaseQualityParser()
        p.handle(s)

        assert p.data == snapshot

    def test_composite(self, snapshot: SnapshotAssertion):
        left_s = StringIO(
            textwrap.dedent(
                """
                #Base	Mean	Median	Lower Quartile	Upper Quartile	10th Percentile	90th Percentile
                1	33.45152	34.0	34.0	34.0	34.0	34.0
                2	33.751	34.0	34.0	34.0	34.0	34.0
                3	33.8779	34.0	34.0	34.0	34.0	34.0
                4	33.85192	34.0	34.0	34.0	34.0	34.0
                5	33.78398	34.0	34.0	34.0	34.0	34.0
                6	37.63014	38.0	38.0	38.0	37.0	38.0
                7	37.54666	38.0	38.0	38.0	37.0	38.0
                8	37.38808	38.0	38.0	38.0	37.0	38.0
                9	37.4646	38.0	38.0	38.0	37.0	38.0
                10-14	37.521139999999995	38.0	38.0	38.0	36.8	38.0
                15-19	37.257456000000005	38.0	38.0	38.0	36.4	38.0
                20-24	37.51578000000001	38.0	38.0	38.0	37.0	38.0
                25-29	37.425292	38.0	38.0	38.0	37.0	38.0
                30-34	37.165183999999996	38.0	37.8	38.0	36.4	38.0
                >>END_MODULE
                """
            )
        )

        right_s = StringIO(
            textwrap.dedent(
                """
                #Base	Mean	Median	Lower Quartile	Upper Quartile	10th Percentile	90th Percentile
                1	32.51418	34.0	34.0	34.0	31.0	34.0
                2	32.70134	34.0	34.0	34.0	31.0	34.0
                3	33.45732	34.0	34.0	34.0	34.0	34.0
                4	33.54688	34.0	34.0	34.0	34.0	34.0
                5	33.64788	34.0	34.0	34.0	34.0	34.0
                6	37.28408	38.0	38.0	38.0	37.0	38.0
                7	37.01514	38.0	38.0	38.0	36.0	38.0
                8	37.10676	38.0	38.0	38.0	36.0	38.0
                9	37.29058	38.0	38.0	38.0	37.0	38.0
                10-14	37.246032	38.0	38.0	38.0	36.6	38.0
                15-19	36.977244	38.0	38.0	38.0	36.0	38.0
                20-24	36.742496	38.0	37.6	38.0	34.8	38.0
                25-29	37.253972000000005	38.0	38.0	38.0	37.0	38.0
                30-34	37.156079999999996	38.0	38.0	38.0	36.4	38.0
                >>END_MODULE
                """
            )
        )

        left_parser = BaseQualityParser()
        right_parser = BaseQualityParser()

        left_parser.handle(left_s)
        right_parser.handle(right_s)

        composite_parser = left_parser.composite(right_parser)

        # Ensure composite points contains values that are all means of the values in
        # left and right points.
        for attr_name in (
            "mean",
            "median",
            "lower_quartile",
            "upper_quartile",
            "tenth_percentile",
            "ninetieth_percentile",
        ):
            for left_point, right_point, composite_point in zip(
                left_parser.data, right_parser.data, composite_parser.data
            ):
                assert (
                    getattr(composite_point, attr_name)
                    == (
                        getattr(left_point, attr_name) + getattr(right_point, attr_name)
                    )
                    / 2
                )

        assert composite_parser.data == snapshot


class TestBasicStatisticsParser:
    async def test_ok(self):
        """Test that the parser works as expected."""
        s = StringIO(
            textwrap.dedent(
                """
                #Measure	Value
                Filename	paired_small_1.fq.gz
                File type	Conventional base calls
                Encoding	Sanger / Illumina 1.9
                Total Sequences	50000
                Sequences flagged as poor quality	0
                Sequence length	50-301
                %GC	41
                >>END_MODULE
                """
            )
        )

        p = BasicStatisticsParser()
        p.handle(s)

        assert p.count == 50000
        assert p.encoding == "Sanger / Illumina 1.9"
        assert p.gc == 41.0
        assert p.length == [50, 301]

    async def test_one_length(self):
        """
        Test that the parser gets the right length range when there is only one length.

        For example:

        36-75 -> [36, 75]
        74 -> [74, 74]
        """
        s = StringIO(
            textwrap.dedent(
                """
                #Measure	Value
                Filename	paired_small_1.fq.gz
                File type	Conventional base calls
                Encoding	Sanger / Illumina 1.9
                Total Sequences	50000
                Sequences flagged as poor quality	0
                Sequence length	74
                %GC	41
                >>END_MODULE
                """
            )
        )

        p = BasicStatisticsParser()
        p.handle(s)

        assert p.count == 50000
        assert p.encoding == "Sanger / Illumina 1.9"
        assert p.gc == 41.0
        assert p.length == [74, 74]

    async def test_composite(self):
        """Test that a composite parser contains the expected values."""
        left = StringIO(
            textwrap.dedent(
                """
                #Measure	Value
                Filename	paired_small_1.fq.gz
                File type	Conventional base calls
                Encoding	Sanger / Illumina 1.9
                Total Sequences	50000
                Sequences flagged as poor quality	0
                Sequence length	36-73
                %GC	39
                >>END_MODULE
                """
            )
        )

        right = StringIO(
            textwrap.dedent(
                """
                #Measure	Value
                Filename	paired_small_2.fq.gz
                File type	Conventional base calls
                Encoding	Sanger / Illumina 1.9
                Total Sequences	50000
                Sequences flagged as poor quality	0
                Sequence length	76
                %GC	45
                >>END_MODULE
                """
            )
        )

        left_parser = BasicStatisticsParser()
        right_parser = BasicStatisticsParser()

        left_parser.handle(left)
        right_parser.handle(right)

        composite = left_parser.composite(right_parser)

        assert composite.count == 100000
        assert composite.encoding == "Sanger / Illumina 1.9"
        assert composite.gc == 42.0
        assert composite.length == [36, 76]


class TestNucleotideCompositionParser:
    async def test_ok(self, snapshot: SnapshotAssertion):
        """Test that the parser works as expected."""
        s = StringIO(
            textwrap.dedent(
                """
                #Base	G	A	T	C
                1	37.191123022882785	24.890865160098272	14.308338916976304	23.60967290004264
                2	13.070834585712854	23.184049694419397	42.773269211501855	20.971846508365896
                3	16.660665706513043	29.670747319571134	31.971115378460553	21.697471595455273
                4	11.83	19.81	42.266	26.094
                5	12.028	38.272	38.278	11.422
                6	26.285999999999998	41.122	20.418	12.174
                7	22.445999999999998	33.274	28.17	16.11
                
                8	21.552	37.602000000000004	24.662	16.184
                9	23.636	17.427999999999997	25.94	32.995999999999995
                10-14	22.150843016860335	25.959319186383727	30.841816836336726	21.04802096041921
                15-19	20.24078495896623	30.798001484840583	28.22802335614102	20.73319020005217
                20-24	20.59303318276372	29.239630135833295	29.784726870463373	20.382609810939613
                25-29	20.523600000000002	29.376799999999996	29.6272	20.4724
                30-34	20.7208	29.4348	29.2532	20.5912
                >>END_MODULE
                """
            )
        )

        p = NucleotideCompositionParser()
        p.handle(s)

        assert p.data == snapshot

    async def test_composite(self, snapshot: SnapshotAssertion):
        left = StringIO(
            textwrap.dedent(
                """
                #Base	G	A	T	C
                1	36.794	25.266	14.288	23.652
                2	13.006	22.822	42.698	21.474
                3	16.252	29.566	32.006	22.176000000000002
                4	11.472	20.148	42.584	25.796000000000003
                5	11.63	37.653999999999996	39.128	11.588
                6	26.306	41.068	20.663999999999998	11.962
                7	22.296	32.424	28.782000000000004	16.497999999999998
                8	21.628	37.422	24.85	16.1
                9	23.592	17.37	26.144000000000002	32.894
                10-14	22.0332	25.753999999999998	31.04	21.1728
                15-19	20.158	30.8324	28.182000000000002	20.8276
                20-24	20.4288	28.9144	30.0688	20.588
                25-29	20.3036	29.2612	29.872799999999998	20.5624
                30-34	20.6264	29.292	29.4056	20.676
                >>END_MODULE
                """
            )
        )

        right = StringIO(
            textwrap.dedent(
                """
                #Base	G	A	T	C
                1	37.191123022882785	24.890865160098272	14.308338916976304	23.60967290004264
                2	13.070834585712854	23.184049694419397	42.773269211501855	20.971846508365896
                3	16.660665706513043	29.670747319571134	31.971115378460553	21.697471595455273
                4	11.83	19.81	42.266	26.094
                5	12.028	38.272	38.278	11.422
                6	26.285999999999998	41.122	20.418	12.174
                7	22.445999999999998	33.274	28.17	16.11

                8	21.552	37.602000000000004	24.662	16.184
                9	23.636	17.427999999999997	25.94	32.995999999999995
                10-14	22.150843016860335	25.959319186383727	30.841816836336726	21.04802096041921
                15-19	20.24078495896623	30.798001484840583	28.22802335614102	20.73319020005217
                20-24	20.59303318276372	29.239630135833295	29.784726870463373	20.382609810939613
                25-29	20.523600000000002	29.376799999999996	29.6272	20.4724
                30-34	20.7208	29.4348	29.2532	20.5912
                >>END_MODULE
                """
            )
        )

        left_parser = NucleotideCompositionParser()
        right_parser = NucleotideCompositionParser()

        left_parser.handle(left)
        right_parser.handle(right)

        composite_parser = left_parser.composite(right_parser)

        for attr_name in (
            "g",
            "a",
            "t",
            "c",
        ):
            for left_point, right_point, composite_point in zip(
                left_parser.data, right_parser.data, composite_parser.data
            ):
                assert (
                    getattr(composite_point, attr_name)
                    == (
                        getattr(left_point, attr_name) + getattr(right_point, attr_name)
                    )
                    / 2
                )

        assert composite_parser.data == snapshot


class TestSequenceQualityParser:
    async def test_ok(self, snapshot: SnapshotAssertion):
        """Test that the parser works as expected."""
        s = StringIO(
            textwrap.dedent(
                """
                #Quality	Count
                17	2.0
                18	0.0
                19	5.0
                20	14.0
                21	17.0
                22	23.0
                23	48.0
                24	62.0
                25	209.0
                26	248.0
                27	359.0
                28	479.0
                29	696.0
                30	969.0
                31	1257.0
                32	1785.0
                33	2392.0
                34	3689.0
                35	5949.0
                36	10202.0
                37	21595.0
                >>END_MODULE
                """
            )
        )

        p = SequenceQualityParser()
        p.handle(s)

        assert p.data == snapshot

    async def test_composite(self, snapshot: SnapshotAssertion):
        """Test that the composite parser contains the averaged qualities for each."""
        left = StringIO(
            textwrap.dedent(
                """
                #Quality	Count
                17	2.0
                18	0.0
                19	5.0
                20	14.0
                21	17.0
                22	23.0
                23	48.0
                24	62.0
                25	209.0
                26	248.0
                27	359.0
                28	479.0
                29	696.0
                30	969.0
                31	1257.0
                32	1785.0
                33	2392.0
                34	3689.0
                35	5949.0
                36	10202.0
                37	21595.0
                >>END_MODULE
                """
            )
        )

        right = StringIO(
            textwrap.dedent(
                """
                #Quality	Count
                12	1.0
                13	2.0
                14	0.0
                15	2.0
                16	10.0
                17	21.0
                18	41.0
                19	57.0
                20	69.0
                21	117.0
                22	171.0
                23	240.0
                24	369.0
                25	469.0
                26	602.0
                27	791.0
                28	955.0
                29	1350.0
                30	1729.0
                31	2211.0
                32	3000.0
                33	4079.0
                34	5505.0
                35	6578.0
                36	8050.0
                37	13581.0
                >>END_MODULE
                """
            )
        )

        left_parser = SequenceQualityParser()
        right_parser = SequenceQualityParser()

        left_parser.handle(left)
        right_parser.handle(right)

        composite_parser = left_parser.composite(right_parser)

        for left_point, right_point, composite_point in zip(
            left_parser.data, right_parser.data, composite_parser.data
        ):
            assert left_point + right_point == composite_point

        assert composite_parser.data == snapshot


async def test_fastqc(
    example_path: Path,
    run_subprocess: RunSubprocess,
    snapshot: SnapshotAssertion,
    work_path: Path,
):
    shutil.copyfile(
        example_path / "sample/reads_1.fq.gz",
        work_path / "reads_1.fq.gz",
    )

    shutil.copyfile(
        example_path / "sample/reads_2.fq.gz",
        work_path / "reads_2.fq.gz",
    )

    output_path = work_path / "fastqc"

    async for func in fastqc(run_subprocess, work_path):
        out = await func(
            (
                work_path / "reads_1.fq.gz",
                work_path / "reads_2.fq.gz",
            ),
            output_path,
        )

        assert out == snapshot
