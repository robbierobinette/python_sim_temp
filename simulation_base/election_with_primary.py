"""
Election with primary system implementation.
"""
from typing import List
from .candidate import Candidate
from .election_result import ElectionResult
from .population_tag import DEMOCRATS, REPUBLICANS
from .simple_plurality import SimplePlurality
from .voter import Voter
from .election_result import CandidateResult
from .ballot import RCVBallot
from .election_process import ElectionProcess


class ElectionWithPrimaryResult(ElectionResult):
    """Result of an election with primaries."""
    
    def __init__(self, democratic_primary: ElectionResult, republican_primary: ElectionResult, 
                 general_election: ElectionResult):
        """Initialize election with primary result."""
        self.democratic_primary = democratic_primary
        self.republican_primary = republican_primary
        self.general_election = general_election
    
    def winner(self) -> Candidate:
        """Winner of the general election."""
        return self.general_election.winner()
    
    def voter_satisfaction(self) -> float:
        """Voter satisfaction from general election."""
        return self.general_election.voter_satisfaction()
    
    def ordered_results(self) -> List[CandidateResult]:
        """Ordered results of the general election."""
        return self.general_election.ordered_results()
    
    @property
    def n_votes(self) -> float:
        """Total votes in general election."""
        return self.general_election.n_votes

    def print_details(self) -> None:
        """Print details of the election with primary."""
        print("Democratic primary result:")
        self.democratic_primary.print_details()
        print("Republican primary result:")
        self.republican_primary.print_details()
        print("General election result:")
        self.general_election.print_details()
 

class ElectionWithPrimary(ElectionProcess):
    """Election process with separate Democratic and Republican primaries."""
    
    def __init__(self, primary_skew: float = 0.5, debug: bool = False):
        """Initialize primary election process."""
        self.primary_skew = primary_skew
        self.debug = debug
        self.dem_primary_factions = {DEMOCRATS}  # Could add Progressive, etc.
        self.rep_primary_factions = {REPUBLICANS}


   
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "primary"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionWithPrimaryResult:
        """Run election with primaries."""
        # Separate voters by party
        dem_voters = [ballot.voter for ballot in ballots if ballot.voter.party.tag == DEMOCRATS]
        rep_voters = [ballot.voter for ballot in ballots if ballot.voter.party.tag == REPUBLICANS]
        
        # Create skewed populations for primaries if primary_skew > 0
        if self.primary_skew > 0:
            primary_dem_voters = self._create_skewed_voters(dem_voters, -self.primary_skew)
            primary_rep_voters = self._create_skewed_voters(rep_voters, self.primary_skew)
        else:
            primary_dem_voters = dem_voters
            primary_rep_voters = rep_voters
        
        # Filter candidates by party
        dem_candidates = [c for c in candidates 
                         if c.tag in self.dem_primary_factions]
        rep_candidates = [c for c in candidates 
                         if c.tag in self.rep_primary_factions]
        
        # Create ballots for primaries (skewed if needed)
        if self.primary_skew > 0:
            # Create new ballots for skewed voters
            # Use config from first ballot (assuming all ballots have same config)
            config = ballots[0].config
            dem_ballots = [RCVBallot(voter, dem_candidates, config, ballots[0].gaussian_generator) 
                          for voter in primary_dem_voters]
            rep_ballots = [RCVBallot(voter, rep_candidates, config, ballots[0].gaussian_generator) 
                          for voter in primary_rep_voters]
        else:
            # Use original ballots filtered by party
            dem_ballots = [ballot for ballot in ballots if ballot.voter.party.tag == DEMOCRATS]
            rep_ballots = [ballot for ballot in ballots if ballot.voter.party.tag == REPUBLICANS]
        
        # Run Democratic primary
        dem_primary_result = self._run_primary(dem_candidates, dem_ballots)
        # Run Republican primary
        rep_primary_result = self._run_primary(rep_candidates, rep_ballots)
        # Get primary winners
        dem_winner = dem_primary_result.ordered_results()[0].candidate
        rep_winner = rep_primary_result.ordered_results()[0].candidate
        
        # Find other candidates (independents, etc.)
        primary_candidates = set(dem_candidates + rep_candidates)
        other_candidates = [c for c in candidates 
                           if c not in primary_candidates]
        
        # Run general election with primary winners + others
        final_candidates = other_candidates + [dem_winner, rep_winner]
        general_result = self._run_general(final_candidates, ballots)
        if self.debug:
            self._print_debug_results_from_ballots(candidates, 
                dem_primary_result, 
                rep_primary_result, 
                primary_dem_voters,
                primary_rep_voters,
                general_result)
        
        return ElectionWithPrimaryResult(dem_primary_result, rep_primary_result, general_result)
    
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
    
    def _run_primary(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run a primary election."""
        # Use simple plurality for primaries
        primary_process = SimplePlurality()
        return primary_process.run(candidates, ballots)
    
    def _run_general(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run general election."""
        general_process = SimplePlurality(debug=False)
        result = general_process.run(candidates, ballots)
        result._voter_satisfaction = self.voter_satisfaction(result.winner(), ballots)
        return result

    def _print_debug_results_from_ballots(self, candidates: List[Candidate], dem_result: ElectionResult, rep_result: ElectionResult, 
                                        dem_primary_voters: List[Voter], rep_primary_voters: List[Voter],
                                        general_result: ElectionResult) -> None:
        """Print debug information."""

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
        
        print("General Election:")
        for cr in general_result.ordered_results():
            print(f"{cr.candidate.name:12s} {cr.candidate.ideology:5.2f} {cr.candidate.quality:5.2f} {cr.votes:8.0f}")

