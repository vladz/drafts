from typing import List

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class DeepSales():
    TtNumber: str
    Sdd: int


@dataclass(frozen=True)
class ListDeepSales(DataClassJsonMixin):
    SddTts: List[DeepSales]