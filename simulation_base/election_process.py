"""
Abstract base class for election processes.
"""
from abc import ABC, abstractmethod
from typing import List
from .election_result import ElectionResult
from .ballot import RCVBallot
from .candidate import Candidate


class ElectionProcess(ABC):
    """Abstract base class for all election processes."""
    
    @abstractmethod
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run an election with the given candidates and ballots.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            ElectionResult with winner, voter_satisfaction, and ordered_results
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the election process."""
        pass

    def voter_satisfaction(self, winner: Candidate, ballots: List[RCVBallot]):
        left_voter_count = sum(1 for ballot in ballots if ballot.voter.ideology < winner.ideology)
        return 1 - abs((2.0 * left_voter_count / len(ballots)) - 1) 

