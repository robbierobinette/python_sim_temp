"""
Top-2 primary election implementation.
"""
from typing import List
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .ballot import RCVBallot
from .candidate import Candidate
from .simple_plurality import SimplePlurality


class Top2PrimaryResult(ElectionResult):
    """Result of a top-2 primary election."""
    
    def __init__(self, primary_result: ElectionResult, all_candidates: List[Candidate]):
        """Initialize top-2 primary result.
        
        Args:
            primary_result: Results from the single primary election
            all_candidates: All candidates in the election
        """
        self.primary_result = primary_result
        self._all_candidates = all_candidates
        
        # Get top 2 candidates from primary results
        ordered_results = primary_result.ordered_results()
        self._top2_candidates = [result.candidate for result in ordered_results[:2]]
    
    def winner(self) -> Candidate:
        """Return the top candidate from the primary."""
        if self._top2_candidates:
            return self._top2_candidates[0]
        else:
            raise ValueError("No candidates in top-2 primary result")
    
    def voter_satisfaction(self) -> float:
        """Return 0 (not calculated for primaries)."""
        return 0.0
    
    def ordered_results(self) -> List[CandidateResult]:
        """Return results for the top 2 candidates."""
        results = []
        
        # Add top 2 candidates with their vote counts
        ordered_primary_results = self.primary_result.ordered_results()
        for result in ordered_primary_results[:2]:
            results.append(CandidateResult(candidate=result.candidate, votes=result.votes))
        
        return results
    
    @property
    def n_votes(self) -> float:
        """Total votes in the primary."""
        return self.primary_result.n_votes
    
    @property
    def top2_candidates(self) -> List[Candidate]:
        """Get the top 2 candidates that will advance to the general election."""
        return self._top2_candidates.copy()


class Top2Primary(ElectionProcess):
    """Top-2 primary election process where all voters vote in the same primary."""
    
    def __init__(self, debug: bool = False):
        """Initialize top-2 primary election.
        
        Args:
            debug: Whether to enable debug output
        """
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "top2Primary"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> Top2PrimaryResult:
        """Run top-2 primary election where all voters vote in the same primary.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            Top2PrimaryResult with top 2 candidates advancing to general election
        """
        if self.debug:
            print("Running top-2 primary election")
            print(f"All candidates: {[c.name for c in candidates]}")
            print(f"Total ballots: {len(ballots)}")
        
        # Run single primary election using simple plurality
        primary_process = SimplePlurality(debug=self.debug)
        primary_result = primary_process.run(candidates, ballots)
        
        if self.debug:
            print("Primary results:")
            for result in primary_result.ordered_results():
                print(f"  {result.candidate.name}: {result.votes}")
            
            top2 = [result.candidate.name for result in primary_result.ordered_results()[:2]]
            print(f"Top 2 candidates advancing: {top2}")
        
        return Top2PrimaryResult(primary_result, candidates)
