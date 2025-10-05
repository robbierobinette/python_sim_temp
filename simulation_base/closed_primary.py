"""
Closed primary election implementation.
"""
from typing import List, Optional
from dataclasses import dataclass
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .candidate import Candidate
from .population_tag import DEMOCRATS, REPUBLICANS
from .simple_plurality import SimplePlurality
from .plurality_with_runoff import PluralityWithRunoff
from .ballot import RCVBallot


@dataclass
class ClosedPrimaryConfig:
    """Configuration for closed primary elections."""
    use_runoff: bool = False
    primary_skew: float = 0.0


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
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ClosedPrimaryResult:
        """Run closed primary election with separate Democratic and Republican primaries.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            ClosedPrimaryResult with winners from both party primaries
        """
        if self.debug:
            print(f"Running closed primary with runoff: {self.config.use_runoff}")
        
        # Separate voters by party
        dem_voters = [ballot.voter for ballot in ballots if ballot.voter.party.tag == DEMOCRATS]
        rep_voters = [ballot.voter for ballot in ballots if ballot.voter.party.tag == REPUBLICANS]
        
        if self.debug:
            print(f"Democratic voters: {len(dem_voters)}, Republican voters: {len(rep_voters)}")
        
        # Create skewed populations for primaries if primary_skew > 0
        if self.config.primary_skew > 0:
            primary_dem_voters = self._create_skewed_voters(dem_voters, -self.config.primary_skew)
            primary_rep_voters = self._create_skewed_voters(rep_voters, self.config.primary_skew)
        else:
            primary_dem_voters = dem_voters
            primary_rep_voters = rep_voters
        
        # Filter candidates by party
        dem_candidates = [c for c in candidates if c.tag == DEMOCRATS]
        rep_candidates = [c for c in candidates if c.tag == REPUBLICANS]
        
        if self.debug:
            print(f"Democratic candidates: {[c.name for c in dem_candidates]}")
            print(f"Republican candidates: {[c.name for c in rep_candidates]}")
        
        # Create ballots for primaries (skewed if needed)
        if self.config.primary_skew > 0:
            # Create new ballots for skewed voters
            from .ballot import RCVBallot
            from .election_config import ElectionConfig
            # Use config from first ballot (assuming all ballots have same config)
            config = ElectionConfig(uncertainty=0.1)  # Default config
            dem_ballots = [RCVBallot(voter, dem_candidates, config, ballots[0].gaussian_generator) 
                          for voter in primary_dem_voters]
            rep_ballots = [RCVBallot(voter, rep_candidates, config, ballots[0].gaussian_generator) 
                          for voter in primary_rep_voters]
        else:
            # Use original ballots filtered by party
            dem_ballots = [ballot for ballot in ballots if ballot.voter.party.tag == DEMOCRATS]
            rep_ballots = [ballot for ballot in ballots if ballot.voter.party.tag == REPUBLICANS]
        
        # Run Democratic primary
        dem_primary_result = self._run_party_primary(dem_candidates, dem_ballots, "Democratic")
        
        # Run Republican primary
        rep_primary_result = self._run_party_primary(rep_candidates, rep_ballots, "Republican")
        
        if self.debug:
            self._print_debug_results_from_ballots(candidates, dem_primary_result, rep_primary_result, 
                                                 primary_dem_voters, primary_rep_voters)
        
        return ClosedPrimaryResult(dem_primary_result, rep_primary_result, candidates)
    
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
    
    def _run_party_primary(self, candidates: List[Candidate], ballots: List[RCVBallot], 
                          party_name: str) -> ElectionResult:
        """Run a party primary election."""
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
    
    def _print_debug_results_from_ballots(self, candidates: List[Candidate], dem_result: ElectionResult, rep_result: ElectionResult, 
                                        dem_primary_voters: List, rep_primary_voters: List) -> None:
        """Print debug information matching ElectionWithPrimary format."""
        
        # Calculate population centers
        dm = sum([v.ideology for v in dem_primary_voters]) / len(dem_primary_voters) if dem_primary_voters else 0.0
        rm = sum([v.ideology for v in rep_primary_voters]) / len(rep_primary_voters) if rep_primary_voters else 0.0

        # Calculate overall population centers from original voters
        all_voters = dem_primary_voters + rep_primary_voters
        dem_mean = sum([v.ideology for v in all_voters if v.party.tag == DEMOCRATS]) / len([v for v in all_voters if v.party.tag == DEMOCRATS]) if any(v.party.tag == DEMOCRATS for v in all_voters) else 0.0
        rep_mean = sum([v.ideology for v in all_voters if v.party.tag == REPUBLICANS]) / len([v for v in all_voters if v.party.tag == REPUBLICANS]) if any(v.party.tag == REPUBLICANS for v in all_voters) else 0.0
        median_voter = sum([v.ideology for v in all_voters]) / len(all_voters) if all_voters else 0.0

        print(f"Democratic population center: {dem_mean:.2f} {dm:.2f}")
        print(f"Republican population center: {rep_mean:.2f} {rm:.2f}")
        print(f"median voter: {median_voter:.2f}")

        print("Democratic Primary:")
        for cr in dem_result.ordered_results():
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.candidate.quality:5.2f} {cr.votes:8.0f} {cr.candidate.affinity_string()}")
        
        print("Republican Primary:")
        for cr in rep_result.ordered_results():
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.candidate.quality:5.2f} {cr.votes:8.0f} {cr.candidate.affinity_string()}")
