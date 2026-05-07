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
    html_signal: str | None = None


class Heuristic(ABC):
    """
    A single payjoin detection heuristic.
    """

    name: str = "unnamed"

    @abstractmethod
    def check(self, tx: Transaction) -> HeuristicResult:
        """
        Analyse tx and return a scored result.
        """
