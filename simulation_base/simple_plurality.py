"""
Simple plurality voting implementation for primaries.
"""
from typing import List
from .election_result import ElectionResult, CandidateResult
from .ballot import RCVBallot
from .candidate import Candidate


class SimplePlurality:
    """Simple plurality voting election process."""
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "simplePlurality"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run simple plurality election."""
        # Count first-choice votes
        results = {}
        for ballot in ballots:
            # Get first choice candidate
            first_choice = ballot.candidate(set(candidates))
            if first_choice:
                results[first_choice] = results.get(first_choice, 0.0) + ballot.weight
        
        # Ensure all candidates are in results (with 0 votes if needed)
        for candidate in candidates:
            if candidate not in results:
                results[candidate] = 0.0
        
        return ElectionResult(results, 0.0)
