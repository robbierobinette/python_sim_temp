"""
Top-N primary election implementation.
"""
from typing import List
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .ballot import RCVBallot
from .candidate import Candidate
from .simple_plurality import SimplePlurality


class TopNPrimaryResult(ElectionResult):
    """Result of a top-N primary election."""
    
    def __init__(self, primary_result: ElectionResult, all_candidates: List[Candidate], n: int):
        """Initialize top-N primary result.
        
        Args:
            primary_result: Results from the single primary election
            all_candidates: All candidates in the election
            n: Number of top candidates to advance
        """
        self.primary_result = primary_result
        self._all_candidates = all_candidates
        self.n = n
        
        # Get top N candidates from primary results
        ordered_results = primary_result.ordered_results()
        self._topn_candidates = [result.candidate for result in ordered_results[:n]]
    
    def winner(self) -> Candidate:
        """Return the top candidate from the primary."""
        if self._topn_candidates:
            return self._topn_candidates[0]
        else:
            raise ValueError("No candidates in top-N primary result")
    
    def voter_satisfaction(self) -> float:
        """Return 0 (not calculated for primaries)."""
        return 0.0
    
    def ordered_results(self) -> List[CandidateResult]:
        """Return results for the top N candidates."""
        results = []
        
        # Add top N candidates with their vote counts
        ordered_primary_results = self.primary_result.ordered_results()
        for result in ordered_primary_results[:self.n]:
            results.append(CandidateResult(candidate=result.candidate, votes=result.votes))
        
        return results
    
    @property
    def n_votes(self) -> float:
        """Total votes in the primary."""
        return self.primary_result.n_votes
    
    @property
    def topn_candidates(self) -> List[Candidate]:
        """Get the top N candidates that will advance to the general election."""
        return self._topn_candidates.copy()


class TopNPrimary(ElectionProcess):
    """Top-N primary election process where all voters vote in the same primary."""
    
    def __init__(self, n: int = 2, debug: bool = False):
        """Initialize top-N primary election.
        
        Args:
            n: Number of top candidates to advance to general election
            debug: Whether to enable debug output
        """
        self.n = n
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return f"top{self.n}Primary"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> TopNPrimaryResult:
        """Run top-N primary election where all voters vote in the same primary.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            TopNPrimaryResult with top N candidates advancing to general election
        """
        if self.debug:
            print(f"Running top-{self.n} primary election")
            print(f"All candidates: {[c.name for c in candidates]}")
            print(f"Total ballots: {len(ballots)}")
        
        # Run single primary election using simple plurality
        primary_process = SimplePlurality(debug=self.debug)
        primary_result = primary_process.run(candidates, ballots)
        
        if self.debug:
            print("Primary results:")
            for result in primary_result.ordered_results():
                print(f"  {result.candidate.name}: {result.votes}")
            
            topn = [result.candidate.name for result in primary_result.ordered_results()[:self.n]]
            print(f"Top {self.n} candidates advancing: {topn}")
        
        return TopNPrimaryResult(primary_result, candidates, self.n)
