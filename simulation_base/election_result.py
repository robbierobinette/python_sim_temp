"""
Election result representation.
"""
from dataclasses import dataclass
from typing import Dict, List
from .candidate import Candidate


@dataclass
class CandidateResult:
    """Result for a single candidate."""
    candidate: Candidate
    votes: float


class ElectionResult:
    """Base class for election results."""
    
    def __init__(self, results: Dict[Candidate, float], voter_satisfaction: float = 0.0):
        """Initialize election result."""
        self.results = results
        self.voter_satisfaction = voter_satisfaction
    
    @property
    def n_votes(self) -> float:
        """Total number of votes cast."""
        return sum(self.results.values())
    
    @property
    def ordered_results(self) -> List[CandidateResult]:
        """Results ordered by vote count (descending)."""
        return sorted([CandidateResult(candidate=c, votes=v) 
                      for c, v in self.results.items()],
                     key=lambda x: x.votes, reverse=True)
    
    @property
    def winner(self) -> Candidate:
        """The winning candidate."""
        return self.ordered_results[0].candidate
    
    @property
    def candidates(self) -> List[Candidate]:
        """All candidates in the election."""
        return list(self.results.keys())
