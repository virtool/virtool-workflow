from pathlib import Path

from virtool_core.models.subtraction import Subtraction


class WFSubtraction(Subtraction):
    """
    A Virtool subtraction.

    It inherits fields from the core subtraction model and adds attributes for working
    with the subtraction in a workflow.
    """

    path: Path
    """
    The path to the subtraction directory in the workflow work directory.
 
    The subtraction directory contains the FASTA and Bowtie2 files for the subtraction.
    """

    @property
    def fasta_path(self) -> Path:
        """
        The path in the running workflow's work_path to the GZIP-compressed FASTA file
        for the subtraction.

        eg. ``<work_path>/subtractions/<id>/subtraction.fa.gz``

        """
        return self.path / "subtraction.fa.gz"

    @property
    def bowtie2_index_path(self) -> Path:
        """
        The path to Bowtie2 prefix in the the running workflow's work_path

        For example, ``<work_path>/subtractions/<id>/subtraction`` refers to the Bowtie2
        index files:
            - ``<work_path>/subtractions/<id>/subtraction.1.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.2.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.3.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.4.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.rev.1.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.rev.2.bt2``

        """
        return self.path / "subtraction"
