"""
Instant Runoff Voting (IRV) election implementation.
"""
from typing import List, Set, Dict
from .election_result import ElectionResult, CandidateResult
from .candidate import Candidate
from .ballot import RCVBallot
from .voter import Voter
from .election_process import ElectionProcess


class RCVRoundResult(ElectionResult):
    """Result of a single round in IRV."""
    
    def __init__(self, candidates: List[Candidate], results: Dict[Candidate, float], 
                 voter_satisfaction: float = 0.0):
        self._candidates = candidates
        self._results = results
        self._voter_satisfaction = voter_satisfaction
    
    @property
    def candidates(self) -> List[Candidate]:
        """All candidates in this round."""
        return self._candidates
    
    @property
    def active_candidates(self) -> Set[Candidate]:
        """Candidates still active in this round."""
        return set(self._results.keys())
    
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


class RCVResult(ElectionResult):
    """Complete IRV election result with multiple rounds."""
    
    def __init__(self, rounds: List[RCVRoundResult], voter_satisfaction: float = 0.0):
        """Initialize RCV result."""
        self.rounds = rounds
        self._voter_satisfaction = voter_satisfaction
    
    @property
    def all_round_results(self) -> List[CandidateResult]:
        """All results from all rounds."""
        results = []
        if self.rounds:
            # Add final round results
            results.extend(self.rounds[-1].ordered_results())
            # Add eliminated candidates from previous rounds
            for round_result in reversed(self.rounds[:-1]):
                if round_result.ordered_results():
                    results.append(round_result.ordered_results()[-1])
        return results
    
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
    
    def print_detailed_results(self) -> None:
        """Print detailed results for all rounds."""
        for i, round_result in enumerate(self.rounds):
            print(f"Round {i + 1}")
            for candidate_result in round_result.ordered_results():
                print(f"\t{candidate_result.candidate.name:6s} {candidate_result.votes:5.0f}")


class InstantRunoffElection(ElectionProcess):
    """Instant Runoff Voting election process."""
    
    def __init__(self, debug: bool = False):
        """Initialize IRV election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "instantRunoff"
    
    def run(self, election_def) -> RCVResult:
        """Run IRV election with the given election definition."""
        # Generate ballots from population
        ballots = []
        for voter in election_def.population.voters:
            ballot = voter.ballot(election_def.candidates, election_def.config, 
                                 election_def.gaussian_generator)
            ballots.append(ballot)
        
        # Run the election
        rounds = self._compute_rounds([], ballots, set(election_def.candidates), 
                                     election_def.candidates)
        if self.debug:
            self._debug_print(rounds)
        
        # Calculate voter satisfaction
        result = RCVResult(rounds, 0.0)
        if result.rounds:
            winner = result.rounds[-1].winner()
            left_voter_count = sum(1 for v in election_def.population.voters 
                                  if v.ideology < winner.ideology)
            voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(election_def.population.voters)) - 1)
            result._voter_satisfaction = voter_satisfaction
        
        return result
    
    def run_with_ballots(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> RCVResult:
        """Run IRV election with given candidates and ballots (legacy method)."""
        rounds = self._compute_rounds([], ballots, set(candidates), candidates)
        if self.debug:
            self._debug_print(rounds)
        return RCVResult(rounds, 0.0)
    
    def run_with_voters(self, voters: List[Voter], candidates: List[Candidate], 
                       ballots: List[RCVBallot]) -> RCVResult:
        """Run IRV election and calculate voter satisfaction (legacy method)."""
        result = self.run_with_ballots(candidates, ballots)
        
        # Calculate voter satisfaction
        if result.rounds:
            winner = result.rounds[-1].winner()
            left_voter_count = sum(1 for v in voters if v.ideology < winner.ideology)
            voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(voters)) - 1)
            result._voter_satisfaction = voter_satisfaction
        
        return result
    
    def _compute_round_result(self, ballots: List[RCVBallot], 
                             active_candidates: Set[Candidate],
                             candidates: List[Candidate]) -> RCVRoundResult:
        """Compute result for a single round."""
        results = {}
        for ballot in ballots:
            candidate = ballot.candidate(active_candidates)
            if candidate:
                results[candidate] = results.get(candidate, 0.0) + ballot.weight
        
        return RCVRoundResult(candidates, results)
    
    def _compute_rounds(self, prior_rounds: List[RCVRoundResult], 
                       ballots: List[RCVBallot], 
                       active_candidates: Set[Candidate],
                       candidates: List[Candidate]) -> List[RCVRoundResult]:
        """Compute all rounds of IRV."""
        n_weighted_ballots = sum(ballot.weight for ballot in ballots)
        round_result = self._compute_round_result(ballots, active_candidates, candidates)
        
        # Check if we have a majority winner
        if round_result.ordered_results() and round_result.ordered_results()[0].votes / n_weighted_ballots >= 0.5:
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
    
    def _debug_print(self, rounds: List[RCVRoundResult]) -> None:
        """Print debug information for rounds."""
        for round_result in rounds:
            print("Round!")
            for candidate_result in round_result.ordered_results():
                print(f"{candidate_result.candidate.name:20s} "
                      f"{candidate_result.candidate.ideology:6.0f} "
                      f"{candidate_result.votes:8.2f}")
