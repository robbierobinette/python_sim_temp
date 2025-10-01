"""
Election result representation.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List
from .candidate import Candidate


@dataclass
class CandidateResult:
    """Result for a single candidate."""
    candidate: Candidate
    votes: float


class ElectionResult(ABC):
    """Abstract base class for election results."""
    
    @abstractmethod
    def winner(self) -> Candidate:
        """Return the winning candidate."""
        pass
    
    @abstractmethod
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        pass
    
    @abstractmethod
    def ordered_results(self) -> List[CandidateResult]:
        """Return results ordered by vote count (descending)."""
        pass
