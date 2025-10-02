"""
Simple plurality voting implementation for primaries.
"""
from typing import List, Dict
from .election_result import ElectionResult, CandidateResult
from .ballot import RCVBallot
from .candidate import Candidate


class SimplePluralityResult(ElectionResult):
    """Result of a simple plurality election."""
    
    def __init__(self, results: Dict[Candidate, float], voter_satisfaction: float = 0.0):
        """Initialize simple plurality result."""
        self._results = results
        self._voter_satisfaction = voter_satisfaction
    
    def winner(self) -> Candidate:
        """Return the winning candidate."""
        return self.ordered_results()[0].candidate
    
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        return self._voter_satisfaction
    
    def ordered_results(self) -> List[CandidateResult]:
        """Return results ordered by vote count (descending)."""
        return sorted([CandidateResult(candidate=c, votes=v) 
                      for c, v in self._results.items()],
                     key=lambda x: x.votes, reverse=True)
    
    @property
    def n_votes(self) -> float:
        """Total votes in the election."""
        return sum(self._results.values())


class SimplePlurality:
    """Simple plurality voting election process."""
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "simplePlurality"
    
    def run_with_ballots(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> SimplePluralityResult:
        """Run simple plurality election with given ballots."""
        # Count first-choice votes
        results = {}
        for ballot in ballots:
            # Get first choice candidate
            first_choice = ballot.candidate(set(candidates))
            if first_choice:
                results[first_choice] = results.get(first_choice, 0.0) + 1.0
        
        # Ensure all candidates are in results (with 0 votes if needed)
        for candidate in candidates:
            if candidate not in results:
                results[candidate] = 0.0
        
        return SimplePluralityResult(results, 0.0)
