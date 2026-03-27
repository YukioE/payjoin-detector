"""
Heuristic base class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from payjoin_detector.core.transaction import Transaction


@dataclass
class HeuristicResult:
    name: str
    score: float
    signal: str | None


class Heuristic(ABC):
    """
    A single payjoin detection heuristic.
    """

    name: str = "unnamed"

    weight: float = 1.0

    @abstractmethod
    def check(self, tx: Transaction) -> HeuristicResult:
        """
        Analyse tx and return a scored result.
        """
