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

        gsi1_keys: Dict[str, str] = (
            {"gsi1pk": self.gsi1pk, "gsi1sk": self.gsi1sk} if self.gsi1pk and self.gsi1sk else {}
        )

        return {
            "pk": self.pk,
            "sk": self.sk,
            **gsi1_keys,
        }

    def to_item(self) -> dict:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__dict__}>"
