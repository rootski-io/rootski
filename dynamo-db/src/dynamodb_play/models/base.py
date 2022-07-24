from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True, eq=True)
class DynamoModel:

    @property
    def pk(self) -> str:
        """Return the partition key of the model."""
        raise NotImplementedError()

    @property
    def sk(self) -> str:
        """Return the sort key of the model."""
        raise NotImplementedError()

    @property
    def gsi1pk(self) -> Optional[str]:
        """Return the model's partition key in the first global secondary index."""
        return None

    @property
    def gsi1sk(self) -> Optional[str]:
        """Return the model's sort key in the first global secondary index."""
        return None

    @property
    def keys(self) -> Dict[str, str]:

        gsi1_keys: Dict[str, str] = {
            "GSI1PK": self.gsi1pk,
            "GSI1SK": self.gsi1sk
        } if self.gsi1pk and self.gsi1sk else {}

        return {
            "PK": self.pk,
            "SK": self.sk,
            **gsi1_keys,
        }

    def to_dict(self) -> dict:
        raise NotImplementedError()
