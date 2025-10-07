"""
Top-N primary election implementation.
"""
from typing import List

from simulation_base.population_tag import DEMOCRATS, REPUBLICANS
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
    
    def __init__(self, n: int, primary_skew: float, debug: bool = False):
        """Initialize top-N primary election.
        
        Args:
            n: Number of top candidates to advance to general election
            config: Configuration for the primary (skew settings, etc.)
            debug: Whether to enable debug output
        """
        self.n = n
        self.primary_skew = primary_skew
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
            print(f"Running top-{self.n} primary election, skew: {self.primary_skew}")
            print("All candidates: ")
            for c in candidates:
                print(f"  {c.name:12s} {c.ideology:5.2f} {c.quality:5.2f} {c.affinity_string()}")
            print(f"Total ballots: {len(ballots)}")
        
        # Handle primary skew if needed
        if self.primary_skew > 0:
            # Create skewed voters and new ballots for primaries
            primary_ballots = self._create_skewed_ballots(candidates, ballots)
        else:
            # Use original ballots
            primary_ballots = ballots
        
        # Run single primary election using simple plurality
        primary_process = SimplePlurality(debug=self.debug)
        primary_result = primary_process.run(candidates, primary_ballots)
        
        if self.debug:
            print("Primary results:")
            for result in primary_result.ordered_results():
                print(f"  {result.candidate.name}: {result.votes}")
            
            topn = [result.candidate.name for result in primary_result.ordered_results()[:self.n]]
            print(f"Top {self.n} candidates advancing: {topn}")
        
        return TopNPrimaryResult(primary_result, candidates, self.n)
    
    def _create_skewed_ballots(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> List[RCVBallot]:
        """Create new ballots with skewed voters for primaries."""
        from .voter import Voter
        
        skewed_ballots = []
        for ballot in ballots:
            # Create skewed voter
            skew = 0
            if ballot.voter.party.tag == REPUBLICANS:
                skew = self.primary_skew
            elif ballot.voter.party.tag == DEMOCRATS:
                skew = -self.primary_skew

            skewed_voter = Voter(
                party=ballot.voter.party,
                ideology=ballot.voter.ideology + skew
            )
            # Create new ballot with skewed voter
            skewed_ballot = RCVBallot(
                voter=skewed_voter,
                candidates=candidates,
                config=ballot.config,
                gaussian_generator=ballot.gaussian_generator
            )
            skewed_ballots.append(skewed_ballot)
        
        return skewed_ballots
