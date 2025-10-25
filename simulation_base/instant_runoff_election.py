"""
Instant Runoff Voting (IRV) election implementation.
"""
from typing import List, Set, Dict

from simulation_base.simple_plurality import SimplePluralityResult
from simulation_base.simple_plurality import SimplePlurality
from .election_result import ElectionResult, CandidateResult
from .candidate import Candidate
from .ballot import RCVBallot
from .voter import Voter
from .election_process import ElectionProcess




class RCVResult(ElectionResult):
    """Complete IRV election result with multiple rounds."""
    
    def __init__(self, rounds: List[SimplePluralityResult], voter_satisfaction: float = 0.0):
        """Initialize RCV result."""
        self.rounds = rounds
        self._voter_satisfaction = voter_satisfaction
    
    def winner(self) -> Candidate:
        """Return the winning candidate."""
        if self.rounds:
            return self.rounds[-1].winner()
        else:
            raise ValueError("No rounds in RCV result")
    
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        return self._voter_satisfaction
    
    def ordered_results(self) -> List[CandidateResult]:
        """Return results ordered by vote count (descending)."""
        if self.rounds:
            return self.rounds[-1].ordered_results()
        else:
            return []
    
    @property
    def n_votes(self) -> float:
        """Total votes in the election."""
        if self.rounds:
            # Sum up all votes from the first round (before any eliminations)
            return sum(result.votes for result in self.rounds[0].ordered_results())
        else:
            return 0.0
    
    def print_details(self) -> None:
        """Print detailed results for all rounds."""
        for i, round_result in enumerate(self.rounds):
            print(f"Round {i + 1}")
            round_result.print_details()

class InstantRunoffElection(ElectionProcess):
    """Instant Runoff Voting election process."""
    
    def __init__(self, debug: bool):
        """Initialize IRV election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "instantRunoff"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> RCVResult:
        """Run IRV election with the given candidates and ballots."""
        # Run the election
        rounds = self._compute_rounds([], ballots, set(candidates), candidates)
        if self.debug:
            self._debug_print(rounds)
        
        # Calculate voter satisfaction
        result = RCVResult(rounds, 0.0)
        if result.rounds:
            winner = result.rounds[-1].winner()
            left_voter_count = sum(1 for ballot in ballots 
                                  if ballot.voter.ideology < winner.ideology)
            voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(ballots)) - 1)
            result._voter_satisfaction = voter_satisfaction
        
        return result
    
    
    def _compute_round_result(self, ballots: List[RCVBallot], 
                             active_candidates: Set[Candidate],
                             candidates: List[Candidate]) -> SimplePluralityResult:
        # use a simpleplurality here!
        """Compute result for a single round."""
        simple_plurality = SimplePlurality(debug=self.debug)
        return simple_plurality.run(active_candidates, ballots)
    
    def _compute_rounds(self, prior_rounds: List[SimplePluralityResult], 
                       ballots: List[RCVBallot], 
                       active_candidates: Set[Candidate],
                       candidates: List[Candidate]) -> List[SimplePluralityResult]:
        """Compute all rounds of IRV."""
        n_ballots = len(ballots)
        round_result = self._compute_round_result(ballots, active_candidates, candidates)
        
        # Check if we have a majority winner
        if round_result.ordered_results() and round_result.ordered_results()[0].votes / n_ballots >= 0.5:
            return prior_rounds + [round_result]
        else:
            # Eliminate last place candidate
            if round_result.ordered_results():
                eliminated_candidate = round_result.ordered_results()[-1].candidate
                new_candidates = active_candidates - {eliminated_candidate}
                return self._compute_rounds(prior_rounds + [round_result], 
                                          ballots, new_candidates, candidates)
            else:
                return prior_rounds + [round_result]
    
    def _debug_print(self, rounds: List[SimplePluralityResult]) -> None:
        """Print debug information for rounds."""
        for i, round_result in enumerate(rounds):
            print(f"Round {i + 1}")
            round_result.print_details()