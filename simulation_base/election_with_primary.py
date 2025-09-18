"""
Election with primary system implementation.
"""
from dataclasses import dataclass
from typing import List, Set, Optional
from .candidate import Candidate
from .combined_population import CombinedPopulation
from .election_config import ElectionConfig
from .election_definition import ElectionDefinition
from .election_result import ElectionResult
from .gaussian_generator import GaussianGenerator
from .population_tag import PopulationTag, DEMOCRATS, REPUBLICANS
from .simple_plurality import SimplePlurality
from .instant_runoff_election import InstantRunoffElection
from .voter import Voter
from .election_result import CandidateResult
from .ballot import RCVBallot


@dataclass
class ElectionWithPrimaryResult:
    """Result of an election with primaries."""
    democratic_primary: ElectionResult
    republican_primary: ElectionResult
    general_election: ElectionResult
    
    @property
    def winner(self) -> Candidate:
        """Winner of the general election."""
        return self.general_election.winner
    
    @property
    def ordered_results(self) -> List[CandidateResult]:
        """Ordered results of the general election."""
        return self.general_election.ordered_results
    
    @property
    def voter_satisfaction(self) -> float:
        """Voter satisfaction from general election."""
        return self.general_election.voter_satisfaction
    
    @property
    def n_votes(self) -> float:
        """Total votes in general election."""
        return self.general_election.n_votes


class ElectionWithPrimary:
    """Election process with separate Democratic and Republican primaries."""
    
    def __init__(self, primary_skew: float = 0.5, debug: bool = False):
        """Initialize primary election process."""
        self.primary_skew = primary_skew
        self.debug = debug
        self.dem_primary_factions = {DEMOCRATS}  # Could add Progressive, etc.
        self.rep_primary_factions = {REPUBLICANS}  # Could add MAGA, etc.
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "primary"
    
    def run(self, election_def: ElectionDefinition) -> ElectionWithPrimaryResult:
        """Run election with primaries."""
        # Separate voters by party
        dem_voters = [v for v in election_def.population.voters if v.party.tag == DEMOCRATS]
        rep_voters = [v for v in election_def.population.voters if v.party.tag == REPUBLICANS]
        
        # Create skewed populations for primaries
        primary_dem_voters = self._create_skewed_voters(dem_voters, -self.primary_skew)
        primary_rep_voters = self._create_skewed_voters(rep_voters, self.primary_skew)
        
        # Filter candidates by party
        dem_candidates = [c for c in election_def.candidates 
                         if c.tag in self.dem_primary_factions]
        rep_candidates = [c for c in election_def.candidates 
                         if c.tag in self.rep_primary_factions]
        
        # Run Democratic primary
        dem_primary_result = self._run_primary(
            dem_candidates, primary_dem_voters, 
            election_def.config, election_def.gaussian_generator
        )
        
        # Run Republican primary
        rep_primary_result = self._run_primary(
            rep_candidates, primary_rep_voters,
            election_def.config, election_def.gaussian_generator
        )
        
        # Get primary winners
        dem_winner = dem_primary_result.ordered_results[0].candidate
        rep_winner = rep_primary_result.ordered_results[0].candidate
        
        # Find other candidates (independents, etc.)
        primary_candidates = set(dem_candidates + rep_candidates)
        other_candidates = [c for c in election_def.candidates 
                           if c not in primary_candidates]
        
        # Run general election with primary winners + others
        final_candidates = other_candidates + [dem_winner, rep_winner]
        general_result = self._run_general(
            final_candidates, election_def.population.voters,
            election_def.config, election_def.gaussian_generator
        )
        
        if self.debug or dem_primary_result.winner.name == 'D-V' or rep_primary_result.winner.name == 'R-V':
            self._print_debug_results(election_def, 
                dem_primary_result, 
                rep_primary_result, 
                primary_dem_voters,
                primary_rep_voters,
                general_result)
        
        return ElectionWithPrimaryResult(dem_primary_result, rep_primary_result, general_result)
    
    def _create_skewed_voters(self, voters: List, skew: float) -> List:
        """Create voters with skewed ideology for primaries."""
        from .voter import Voter
        from .population_group import PopulationGroup
        
        skewed_voters = []
        for voter in voters:
            # Create new voter with skewed ideology
            skewed_voter = Voter(
                party=voter.party,
                ideology=voter.ideology + skew
            )
            skewed_voters.append(skewed_voter)
        return skewed_voters
    
    def _run_primary(self, candidates: List[Candidate], voters: List, 
                    config: ElectionConfig, gaussian_generator: GaussianGenerator) -> ElectionResult:
        """Run a primary election."""
        # Generate ballots
        ballots = []
        for voter in voters:
            ballot = voter.ballot(candidates, config, gaussian_generator)
            ballots.append(ballot)
        
        # Use simple plurality for primaries
        primary_process = SimplePlurality()
        return primary_process.run(candidates, ballots)
    
    def _run_general(self, candidates: List[Candidate], voters: List,
                    config: ElectionConfig, gaussian_generator: GaussianGenerator) -> ElectionResult:
        """Run general election."""
        # Generate ballots
        ballots = []
        for voter in voters:
            ballot:RCVBallot = voter.ballot(candidates, config, gaussian_generator)
            ballots.append(ballot)
        
        # Use instant runoff for general election
        general_process = InstantRunoffElection(debug=False)
        return general_process.run_with_voters(voters, candidates, ballots)
    
    def _print_debug_results(self, election_def: ElectionDefinition, dem_result: ElectionResult, rep_result: ElectionResult, 
                           dem_primary_voters: List[Voter], rep_primary_voters: List[Voter],
                           general_result: ElectionResult) -> None:
        """Print debug information."""

        dm = sum([v.ideology for v in dem_primary_voters]) / len(dem_primary_voters)
        rm = sum([v.ideology for v in rep_primary_voters]) / len(rep_primary_voters)

        print(f"Democratic population center: {election_def.population.democrats.mean:.2f} {dm:.2f}")
        print(f"Republican population center: {election_def.population.republicans.mean:.2f} {rm:.2f}")
        print(f"median voter: {election_def.population.median_voter:.2f}")


        print("Democratic Primary:")
        for cr in dem_result.ordered_results:
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.votes:8.0f}")
        
        print("Republican Primary:")
        for cr in rep_result.ordered_results:
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.candidate.quality:5.2f} {cr.votes:8.0f}")
        
        # If the winner of the Democratic primary is D-V, print the ideology of every voter that voted for them.
        # dem_primary_winner = dem_result.ordered_results[0].candidate
        # if dem_primary_winner.name == "D-V":
        #     print("Ideologies of voters who voted for D-V in the Democratic primary:")
        #     # For plurality, each voter votes for one candidate; find those who voted for D-V
        #     for voter in dem_primary_voters:
        #         ballot:RCVBallot = voter.ballot(dem_result.candidates, election_def.config, election_def.gaussian_generator)
        #         first_choice = ballot.sorted_candidates[0].candidate
        #         if first_choice.name == "D-V":
        #             print(f"{voter.ideology:.4f}")

        # rep_primary_winner = rep_result.ordered_results[0].candidate
        # if rep_primary_winner.name == "R-V":
        #     print("Ideologies of voters who voted for R-V in the Republican primary:")
        #     for voter in rep_primary_voters:
        #         ballot:RCVBallot = voter.ballot(rep_result.candidates, election_def.config, election_def.gaussian_generator)
        #         first_choice = ballot.sorted_candidates[0].candidate
        #         if first_choice.name == "R-V":
        #             print(f"{voter.ideology:.4f}")
        
        print("General Election:")
        for cr in general_result.ordered_results:
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.candidate.quality:5.2f} {cr.votes:8.0f}")

