from abc import ABC
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NucleotideComposition:
    """
    The nucleotide composition for a sequence.

    https://en.wikipedia.org/wiki/Nucleic_acid_notation

    """
    #: The proportion of adenine (A) bases in the sequence.
    a: float = 0.0
    #: The proportion of cytosine (C) bases in the sequence.
    c: float = 0.0
    #: The proportion of guanine (G) bases in the sequence.
    g: float = 0.0
    #: The proportion of thymine (T) bases in the sequence.
    t: float = 0.0
    #: The proportion of undetermined (N) bases in the sequence.
    n: float = 0.0


@dataclass
class Subtraction(ABC):
    """A dataclass representing a subtraction in Virtool."""

    id: str
    """
    The unique database ID for the subtraction.

    """

    name: str
    """
    The user-defined subtraction name.

    Usually the species name (eg. *Malus domestica*).

    """

    nickname: str
    """
    A user-defined nickname for the subtraction.

    Usually the common name of the species (eg. Apple).
    """

    count: int
    """
    The number of distinct sequences in the subtraction dataset.

    For a plant host, this would be the number of chromosomes and plastid genomes.

    """

    gc: NucleotideComposition
    """
    The nucleotide composition of the subtraction represented as a :class:`.NucleotideComposition` object.
    """

    path: Path
    """
    The path to the subtraction directory in the workflow work directory.
 
    The subtraction directory contains the FASTA and Bowtie2 files for the subtraction.
    """

    @property
    def fasta_path(self) -> Path:
        """
        The path in the running workflow's work_path to the GZIP-compressed FASTA file for the subtraction.

        eg. ``<work_path>/subtractions/<id>/subtraction.fa.gz``

        :type: :class:`.Path`

        """
        return self.path / "subtraction.fa.gz"

    @property
    def bowtie2_index_path(self) -> str:
        """
        The path to Bowtie2 prefix in the the running workflow's work_path

        For example, ``<work_path>/subtractions/<id>/subtraction`` refers to the Bowtie2 index files:
            - ``<work_path>/subtractions/<id>/subtraction.1.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.2.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.3.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.4.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.rev.1.bt2``
            - ``<work_path>/subtractions/<id>/subtraction.rev.2.bt2``

        :type: :class:`.Path`

        """
        return self.path / "subtraction"
