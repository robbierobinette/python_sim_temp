"""
Open primary election implementation.
"""
from typing import List, Optional
from dataclasses import dataclass
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .ballot import RCVBallot
from .candidate import Candidate
from .population_tag import DEMOCRATS, REPUBLICANS
from .simple_plurality import SimplePlurality
from .plurality_with_runoff import PluralityWithRunoff


@dataclass
class OpenPrimaryConfig:
    """Configuration for open primary elections."""
    use_runoff: bool = False
    runoff_threshold: float = 0.5


class OpenPrimaryResult(ElectionResult):
    """Result of an open primary election with cross-party voting."""
    
    def __init__(self, democratic_primary: ElectionResult, republican_primary: ElectionResult, 
                 all_candidates: List[Candidate]):
        """Initialize open primary result.
        
        Args:
            democratic_primary: Results from Democratic primary
            republican_primary: Results from Republican primary
            all_candidates: All candidates in the election
            voter_assignments: Mapping of voter types to candidate names they voted for
        """
        self.democratic_primary = democratic_primary
        self.republican_primary = republican_primary
        self._all_candidates = all_candidates
        
        # Determine winners from each primary
        self._dem_winner = democratic_primary.ordered_results()[0].candidate if democratic_primary.ordered_results() else None
        self._rep_winner = republican_primary.ordered_results()[0].candidate if republican_primary.ordered_results() else None
        
        # Create final candidate list (winners + non-party candidates)
        self._final_candidates = []
        if self._dem_winner:
            self._final_candidates.append(self._dem_winner)
        if self._rep_winner:
            self._final_candidates.append(self._rep_winner)
        
        # Add any candidates that don't belong to major parties
        for candidate in all_candidates:
            if (candidate.tag != DEMOCRATS and candidate.tag != REPUBLICANS and 
                candidate not in self._final_candidates):
                self._final_candidates.append(candidate)
    
    def winner(self) -> Candidate:
        """Return the Democratic primary winner (for compatibility)."""
        if self._dem_winner:
            return self._dem_winner
        elif self._rep_winner:
            return self._rep_winner
        elif self._final_candidates:
            return self._final_candidates[0]
        else:
            raise ValueError("No candidates in open primary result")
    
    def voter_satisfaction(self) -> float:
        """Return 0 (not calculated for primaries)."""
        return 0.0
    
    def ordered_results(self) -> List[CandidateResult]:
        """Return results ordered by party (Dem winner, Rep winner, then others)."""
        results = []
        
        # Add Democratic winner
        if self._dem_winner and self.democratic_primary.ordered_results():
            dem_result = self.democratic_primary.ordered_results()[0]
            results.append(CandidateResult(candidate=self._dem_winner, votes=dem_result.votes))
        
        # Add Republican winner
        if self._rep_winner and self.republican_primary.ordered_results():
            rep_result = self.republican_primary.ordered_results()[0]
            results.append(CandidateResult(candidate=self._rep_winner, votes=rep_result.votes))
        
        # Add other candidates (independents, etc.)
        for candidate in self._final_candidates:
            if candidate not in [self._dem_winner, self._rep_winner]:
                results.append(CandidateResult(candidate=candidate, votes=0.0))
        
        return results
    
    @property
    def n_votes(self) -> float:
        """Total votes across both primaries."""
        dem_votes = self.democratic_primary.n_votes if self.democratic_primary else 0.0
        rep_votes = self.republican_primary.n_votes if self.republican_primary else 0.0
        return dem_votes + rep_votes
    
    @property
    def final_candidates(self) -> List[Candidate]:
        """Get the final candidates that will advance to the general election."""
        return self._final_candidates.copy()
    
    @property
    def democratic_winner(self) -> Optional[Candidate]:
        """Get the Democratic primary winner."""
        return self._dem_winner
    
    @property
    def republican_winner(self) -> Optional[Candidate]:
        """Get the Republican primary winner."""
        return self._rep_winner


class OpenPrimary(ElectionProcess):
    """Open primary election process where voters can vote in any primary."""
    
    def __init__(self, config: Optional[OpenPrimaryConfig] = None, debug: bool = False):
        """Initialize open primary election.
        
        Args:
            config: Configuration for the primary (runoff settings, etc.)
            debug: Whether to enable debug output
        """
        self.config = config or OpenPrimaryConfig()
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "openPrimary"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> OpenPrimaryResult:
        """Run open primary election where voters choose which primary to vote in.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            OpenPrimaryResult with winners from both party primaries
        """
        if self.debug:
            print(f"Running open primary with runoff: {self.config.use_runoff}")
        
        # Filter candidates by party
        dem_candidates = [c for c in candidates if c.tag == DEMOCRATS]
        rep_candidates = [c for c in candidates if c.tag == REPUBLICANS]
        
        if self.debug:
            print(f"Democratic candidates: {[c.name for c in dem_candidates]}")
            print(f"Republican candidates: {[c.name for c in rep_candidates]}")
        
        # Separate ballots by first choice candidate's party
        dem_ballots = []
        rep_ballots = []
        
        for ballot in ballots:
            first_choice = ballot.sorted_candidates[0].candidate
            if first_choice.tag == DEMOCRATS:
                dem_ballots.append(ballot)
            elif first_choice.tag == REPUBLICANS:
                rep_ballots.append(ballot)
        
        if self.debug:
            print(f"Ballots assigned to Democratic primary: {len(dem_ballots)}")
            print(f"Ballots assigned to Republican primary: {len(rep_ballots)}")
        
        # Run Democratic primary
        dem_primary_result = self._run_party_primary(dem_candidates, dem_ballots, "Democratic")
        
        # Run Republican primary
        rep_primary_result = self._run_party_primary(rep_candidates, rep_ballots, "Republican")
        
        if self.debug:
            print(f"Democratic primary winner: {dem_primary_result.ordered_results()[0].candidate.name if dem_primary_result.ordered_results() else 'None'}")
            print(f"Republican primary winner: {rep_primary_result.ordered_results()[0].candidate.name if rep_primary_result.ordered_results() else 'None'}")
        
        return OpenPrimaryResult(dem_primary_result, rep_primary_result, candidates)
    
    def _run_party_primary(self, candidates: List[Candidate], ballots: List[RCVBallot], party_name: str) -> ElectionResult:
        """Run a party primary election with given ballots."""
        if not candidates:
            # Return empty result if no candidates
            from .simple_plurality import SimplePluralityResult
            return SimplePluralityResult({}, 0.0)
        
        if len(candidates) == 1:
            # Single candidate automatically wins
            from .simple_plurality import SimplePluralityResult
            return SimplePluralityResult({candidates[0]: len(ballots)}, 0.0)
        
        primary_process = None
        if self.config.use_runoff:
            # Use plurality with runoff
            primary_process = PluralityWithRunoff(debug=self.debug)
        else:
            # Use simple plurality
            primary_process = SimplePlurality(debug=self.debug)

        return primary_process.run(candidates, ballots)