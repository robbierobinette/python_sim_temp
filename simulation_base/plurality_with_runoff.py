"""
Plurality with runoff voting implementation.
"""
from typing import List
from .election_result import ElectionResult
from .election_process import ElectionProcess
from .election_definition import ElectionDefinition
from .ballot import RCVBallot
from .candidate import Candidate
from .simple_plurality import SimplePlurality


class PluralityWithRunoff(ElectionProcess):
    """Plurality with runoff voting election process."""
    
    def __init__(self, debug: bool = False):
        """Initialize with a SimplePlurality instance."""
        self.simple_plurality = SimplePlurality(debug=debug)
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "pluralityWithRunoff"
    
    def run(self, election_def: ElectionDefinition) -> ElectionResult:
        """Run plurality with runoff election with the given election definition."""
        # Generate ballots from population
        ballots = []
        for voter in election_def.population.voters:
            ballot = voter.ballot(election_def.candidates, election_def.config, 
                                 election_def.gaussian_generator)
            ballots.append(ballot)
        
        # Run the election
        result = self.run_with_ballots(election_def.candidates, ballots)
        
        # Set voter satisfaction to 0 (not calculated for plurality with runoff)
        result._voter_satisfaction = 0.0
        
        return result
    
    def run_with_ballots(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run plurality with runoff election with given ballots."""
        # First round: Use SimplePlurality
        first_round_result = self.simple_plurality.run_with_ballots(candidates, ballots)
        
        # Calculate total votes
        total_votes = first_round_result.n_votes
        
        # Check if top candidate has majority (> 50%)
        if total_votes > 0:
            top_candidate_votes = first_round_result.ordered_results()[0].votes
            if (top_candidate_votes / total_votes) > 0.5:
                # Top candidate has majority, no runoff needed
                return first_round_result
        
        # Runoff needed between top two candidates
        if len(first_round_result.ordered_results()) < 2:
            # Not enough candidates for runoff, return first round results
            return first_round_result
        
        top_candidate = first_round_result.ordered_results()[0].candidate
        second_candidate = first_round_result.ordered_results()[1].candidate
        
        # Run runoff between top two candidates using SimplePlurality
        runoff_candidates = [top_candidate, second_candidate]

        return self.simple_plurality.run_with_ballots(runoff_candidates, ballots)