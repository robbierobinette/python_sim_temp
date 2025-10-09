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
    voter: Optional[Voter] = None
    unsorted_candidates: Optional[List[CandidateScore]] = None
    config: Optional[ElectionConfig] = None
    gaussian_generator: Optional[GaussianGenerator] = None
    
    def __init__(self, voter: Optional[Voter] = None, candidates: Optional[List[Candidate]] = None, 
                 config: Optional[ElectionConfig] = None, gaussian_generator: Optional[GaussianGenerator] = None,
                 unsorted_candidates: Optional[List[CandidateScore]] = None):
        """Initialize ballot with voter and candidates, or with pre-computed candidate scores.
        
        Two initialization patterns are supported:
        1. Production pattern: RCVBallot(voter, candidates, config, gaussian_generator)
           - Computes scores internally based on voter preferences
        2. Test pattern: RCVBallot(unsorted_candidates=scores, gaussian_generator=generator)
           - Uses pre-computed candidate scores
        """
        if unsorted_candidates is not None:
            # Test pattern: use pre-computed scores
            if gaussian_generator is None:
                raise ValueError("gaussian_generator is required when using unsorted_candidates")
            
            self.unsorted_candidates = unsorted_candidates
            self.voter = voter
            self.config = config
            self.gaussian_generator = gaussian_generator
            
            # Sort candidates by score, with random tie-breaking
            def sort_key(cs: CandidateScore) -> tuple:
                return (-cs.score, self.gaussian_generator.next_boolean())
            
            self.sorted_candidates = sorted(self.unsorted_candidates, key=sort_key)
        else:
            # Production pattern: compute scores from voter and candidates
            if voter is None or candidates is None or config is None or gaussian_generator is None:
                raise ValueError("Either provide unsorted_candidates, or provide voter, candidates, config, and gaussian_generator")
            
            self.voter = voter
            self.config = config
            self.gaussian_generator = gaussian_generator
            
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
