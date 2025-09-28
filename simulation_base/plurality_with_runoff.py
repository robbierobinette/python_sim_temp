"""
Plurality with runoff voting implementation.
"""
from typing import List
from .election_result import ElectionResult
from .ballot import RCVBallot
from .candidate import Candidate
from .simple_plurality import SimplePlurality


class PluralityWithRunoff:
    """Plurality with runoff voting election process."""
    
    def __init__(self):
        """Initialize with a SimplePlurality instance."""
        self.simple_plurality = SimplePlurality()
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "pluralityWithRunoff"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run plurality with runoff election."""
        # First round: Use SimplePlurality
        first_round_result = self.simple_plurality.run(candidates, ballots)
        
        # Calculate total votes
        total_votes = first_round_result.n_votes
        
        # Check if top candidate has majority (>= 50%)
        if total_votes > 0:
            top_candidate_votes = first_round_result.ordered_results[0].votes
            if (top_candidate_votes / total_votes) >= 0.5:
                # Top candidate has majority, no runoff needed
                return first_round_result
        
        # Runoff needed between top two candidates
        if len(first_round_result.ordered_results) < 2:
            # Not enough candidates for runoff, return first round results
            return first_round_result
        
        top_candidate = first_round_result.ordered_results[0].candidate
        second_candidate = first_round_result.ordered_results[1].candidate
        
        # Run runoff between top two candidates using SimplePlurality
        runoff_candidates = [top_candidate, second_candidate]

        return self.simple_plurality.run(runoff_candidates, ballots)