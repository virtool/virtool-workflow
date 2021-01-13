from dataclasses import dataclass
from typing import Optional, Literal

DataType = Literal["barcode", "genome"]


@dataclass(frozen=True)
class Reference:
    data_type: DataType
    description: str
    name: str
    organism: str
