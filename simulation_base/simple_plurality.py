"""
Simple plurality voting implementation for primaries.
"""
from typing import List, Dict
from .election_result import ElectionResult, CandidateResult
from .ballot import RCVBallot
from .candidate import Candidate
from .election_process import ElectionProcess


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


class SimplePlurality(ElectionProcess):
    """Simple plurality voting election process."""
    
    def __init__(self, debug: bool = False):
        """Initialize simple plurality election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "simplePlurality"
    
    def run(self, election_def) -> SimplePluralityResult:
        """Run simple plurality election with the given election definition."""
        # Generate ballots from population
        ballots = []
        for voter in election_def.population.voters:
            ballot = voter.ballot(election_def.candidates, election_def.config, 
                                 election_def.gaussian_generator)
            ballots.append(ballot)
        
        # Run the election
        result = self.run_with_ballots(election_def.candidates, ballots)
        
        # Set voter satisfaction to 0 (not calculated for simple plurality)
        result._voter_satisfaction = 0.0
        
        return result
    
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
