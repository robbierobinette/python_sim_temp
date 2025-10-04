"""
Closed primary election implementation.
"""
from typing import List, Optional
from dataclasses import dataclass
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .election_definition import ElectionDefinition
from .candidate import Candidate
from .population_tag import DEMOCRATS, REPUBLICANS
from .simple_plurality import SimplePlurality
from .plurality_with_runoff import PluralityWithRunoff


@dataclass
class ClosedPrimaryConfig:
    """Configuration for closed primary elections."""
    use_runoff: bool = False
    runoff_threshold: float = 0.5
    primary_skew: float = 0.5


class ClosedPrimaryResult(ElectionResult):
    """Result of a closed primary election with separate party primaries."""
    
    def __init__(self, democratic_primary: ElectionResult, republican_primary: ElectionResult, 
                 all_candidates: List[Candidate]):
        """Initialize closed primary result."""
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
            raise ValueError("No candidates in closed primary result")
    
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


class ClosedPrimary(ElectionProcess):
    """Closed primary election process with separate Democratic and Republican primaries."""
    
    def __init__(self, config: Optional[ClosedPrimaryConfig] = None, debug: bool = False):
        """Initialize closed primary election.
        
        Args:
            config: Configuration for the primary (runoff settings, etc.)
            debug: Whether to enable debug output
        """
        self.config = config or ClosedPrimaryConfig()
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "closedPrimary"
    
    def run(self, election_def: ElectionDefinition) -> ClosedPrimaryResult:
        """Run closed primary election with separate Democratic and Republican primaries.
        
        Args:
            election_def: Complete election definition with candidates, population, config, etc.
            
        Returns:
            ClosedPrimaryResult with winners from both party primaries
        """
        if self.debug:
            print(f"Running closed primary with runoff: {self.config.use_runoff}")
        
        # Separate voters by party
        dem_voters = [v for v in election_def.population.voters if v.party.tag == DEMOCRATS]
        rep_voters = [v for v in election_def.population.voters if v.party.tag == REPUBLICANS]
        
        if self.debug:
            print(f"Democratic voters: {len(dem_voters)}, Republican voters: {len(rep_voters)}")
        
        # Create skewed populations for primaries
        primary_dem_voters = self._create_skewed_voters(dem_voters, -self.config.primary_skew)
        primary_rep_voters = self._create_skewed_voters(rep_voters, self.config.primary_skew)
        
        # Filter candidates by party
        dem_candidates = [c for c in election_def.candidates if c.tag == DEMOCRATS]
        rep_candidates = [c for c in election_def.candidates if c.tag == REPUBLICANS]
        
        if self.debug:
            print(f"Democratic candidates: {[c.name for c in dem_candidates]}")
            print(f"Republican candidates: {[c.name for c in rep_candidates]}")
        
        # Run Democratic primary
        dem_primary_result = self._run_party_primary(
            dem_candidates, primary_dem_voters, 
            election_def.config, election_def.gaussian_generator,
            "Democratic"
        )
        
        # Run Republican primary
        rep_primary_result = self._run_party_primary(
            rep_candidates, primary_rep_voters,
            election_def.config, election_def.gaussian_generator,
            "Republican"
        )
        
        if self.debug:
            print(f"Democratic primary winner: {dem_primary_result.ordered_results()[0].candidate.name if dem_primary_result.ordered_results() else 'None'}")
            print(f"Republican primary winner: {rep_primary_result.ordered_results()[0].candidate.name if rep_primary_result.ordered_results() else 'None'}")
        
        return ClosedPrimaryResult(dem_primary_result, rep_primary_result, election_def.candidates)
    
    def _create_skewed_voters(self, voters: List, skew: float) -> List:
        """Create voters with skewed ideology for primaries."""
        from .voter import Voter
        
        skewed_voters = []
        for voter in voters:
            # Create new voter with skewed ideology
            skewed_voter = Voter(
                party=voter.party,
                ideology=voter.ideology + skew
            )
            skewed_voters.append(skewed_voter)
        return skewed_voters
    
    def _run_party_primary(self, candidates: List[Candidate], voters: List, 
                          config, gaussian_generator, party_name: str) -> ElectionResult:
        """Run a party primary election."""
        if not candidates:
            # Return empty result if no candidates
            from .simple_plurality import SimplePluralityResult
            return SimplePluralityResult({}, 0.0)
        
        if len(candidates) == 1:
            # Single candidate automatically wins
            from .simple_plurality import SimplePluralityResult
            return SimplePluralityResult({candidates[0]: len(voters)}, 0.0)
        
        # Generate ballots
        ballots = []
        for voter in voters:
            ballot = voter.ballot(candidates, config, gaussian_generator)
            ballots.append(ballot)
        
        if self.config.use_runoff:
            # Use plurality with runoff
            primary_process = PluralityWithRunoff()
            return primary_process.run_with_ballots(candidates, ballots)
        else:
            # Use simple plurality
            primary_process = SimplePlurality(debug=self.debug)
            return primary_process.run_with_ballots(candidates, ballots)
