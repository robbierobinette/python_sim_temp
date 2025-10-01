"""
Ballot representation for ranked choice voting.
"""
from dataclasses import dataclass
from typing import List, Optional, Set
from .candidate import Candidate
from .gaussian_generator import GaussianGenerator


@dataclass
class CandidateScore:
    """Score for a candidate on a ballot."""
    candidate: Candidate
    score: float


@dataclass
class RCVBallot:
    """Ranked Choice Voting ballot."""
    unsorted_candidates: List[CandidateScore]
    gaussian_generator: Optional[GaussianGenerator] = None
    
    def __post_init__(self):
        """Sort candidates by score after initialization."""
        if self.gaussian_generator is None:
            self.gaussian_generator = GaussianGenerator()
        
        # Sort by score, with random tie-breaking
        def sort_key(cs: CandidateScore) -> tuple:
            # Use negative score for descending order, add random for tie-breaking
            return (-cs.score, self.gaussian_generator.next_boolean())
        
        self.sorted_candidates = sorted(self.unsorted_candidates, key=sort_key)
    
    def candidate(self, active_candidates: Set[Candidate]) -> Optional[Candidate]:
        """Get the highest-ranked active candidate."""
        for candidate_score in self.sorted_candidates:
            if candidate_score.candidate in active_candidates:
                return candidate_score.candidate
        return None
