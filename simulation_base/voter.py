"""
Voter representation and behavior.
"""
from dataclasses import dataclass
from typing import List, Optional
from .population_group import PopulationGroup
from .candidate import Candidate
from .election_config import ElectionConfig
from .gaussian_generator import GaussianGenerator
from .ballot import RCVBallot


@dataclass
class Voter:
    """Represents a voter with party affiliation and ideology."""
    party: PopulationGroup
    ideology: float
    
    def distance_score(self, candidate: Candidate) -> float:
        """Calculate distance-based score for a candidate."""
        return  - abs(self.ideology - candidate.ideology)
    
    def uncertainty(self, config: ElectionConfig, 
                   gaussian_generator: Optional[GaussianGenerator] = None) -> float:
        """Calculate uncertainty factor."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        rg = gaussian_generator()
        return rg * config.uncertainty
    
    def score(self, candidate: Candidate, config: ElectionConfig,
              gaussian_generator: Optional[GaussianGenerator] = None) -> float:
        """Calculate total score for a candidate."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        return (self.distance_score(candidate) +
                candidate.affinity.get(self.party.tag, 0.0) +
                self.uncertainty(config, gaussian_generator) +
                candidate.quality)
    
    def favorite(self, candidates: List[Candidate], config: ElectionConfig,
                gaussian_generator: Optional[GaussianGenerator] = None) -> int:
        """Find the index of the favorite candidate."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        favorite_idx = -1
        favorite_score = -1000.0
        
        for i, candidate in enumerate(candidates):
            score = self.score(candidate, config, gaussian_generator)
            if score > favorite_score:
                favorite_idx = i
                favorite_score = score
        
        return favorite_idx
    
    def ballot(self, candidates: List[Candidate], config: ElectionConfig,
               gaussian_generator: Optional[GaussianGenerator] = None) -> 'RCVBallot':
        """Generate a ranked choice ballot."""
        from .ballot import RCVBallot, CandidateScore
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        scores = []
        for candidate in candidates:
            score = self.score(candidate, config, gaussian_generator)
            scores.append(CandidateScore(candidate=candidate, score=score))
        
        return RCVBallot(unsorted_candidates=scores, gaussian_generator=gaussian_generator)
