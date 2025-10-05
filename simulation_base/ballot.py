"""
Ballot representation for ranked choice voting.
"""
from dataclasses import dataclass
from typing import List, Optional, Set
from .candidate import Candidate
from .gaussian_generator import GaussianGenerator
from .voter import Voter
from .election_config import ElectionConfig


@dataclass
class CandidateScore:
    """Score for a candidate on a ballot."""
    candidate: Candidate
    score: float


@dataclass
class RCVBallot:
    """Ranked Choice Voting ballot."""
    voter: Voter
    unsorted_candidates: List[CandidateScore]
    gaussian_generator: Optional[GaussianGenerator] = None
    
    def __init__(self, voter: Voter, candidates: List[Candidate], 
                 config: ElectionConfig, gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize ballot with voter and candidates, computing scores internally."""
        self.voter = voter
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
        
        # Compute scores for all candidates
        scores = []
        for candidate in candidates:
            score = self._compute_score(candidate, config)
            scores.append(CandidateScore(candidate=candidate, score=score))
        
        self.unsorted_candidates = scores
        
        # Sort candidates by score, with random tie-breaking
        def sort_key(cs: CandidateScore) -> tuple:
            # Use negative score for descending order, add random for tie-breaking
            return (-cs.score, self.gaussian_generator.next_boolean())
        
        self.sorted_candidates = sorted(self.unsorted_candidates, key=sort_key)
    
    def _compute_score(self, candidate: Candidate, config: ElectionConfig) -> float:
        """Compute total score for a candidate (moved from Voter.score)."""
        return (self._distance_score(candidate) +
                candidate.affinity(self.voter.party.tag.short_name) +
                self._uncertainty(config) +
                candidate.quality)
    
    def _distance_score(self, candidate: Candidate) -> float:
        """Calculate distance-based score for a candidate (moved from Voter.distance_score)."""
        return -abs(self.voter.ideology - candidate.ideology)
    
    def _uncertainty(self, config: ElectionConfig) -> float:
        """Calculate uncertainty factor (moved from Voter.uncertainty)."""
        rg = self.gaussian_generator()
        return rg * config.uncertainty
    
    def candidate(self, active_candidates: Set[Candidate]) -> Optional[Candidate]:
        """Get the highest-ranked active candidate."""
        for candidate_score in self.sorted_candidates:
            if candidate_score.candidate in active_candidates:
                return candidate_score.candidate
        return None
