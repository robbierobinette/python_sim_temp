"""
Congressional simulation for all 435 districts.
"""
import csv
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.simulation_config import UnitSimulationConfig, CongressionalSimulationConfigFactory
from simulation_base.election_definition import ElectionDefinition
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.election_with_primary import ElectionWithPrimary, ElectionWithPrimaryResult
from simulation_base.condorcet_election import CondorcetElection
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.election_result import ElectionResult
from simulation_base.election_process import ElectionProcess
from simulation_base.actual_custom_election import ActualCustomElection
from simulation_base.ballot import RCVBallot
from simulation_base.cook_political_data import CookPoliticalData


@dataclass
class DistrictResult:
    """Result for a single district."""
    district: str
    state: str
    incumbent: str
    expected_lean: float
    winner_name: str
    winner_party: str
    winner_ideology: float
    voter_satisfaction: float
    total_votes: float
    margin: float  # Winner's margin over second place


@dataclass
class CongressionalSimulationResult:
    """Complete result of congressional simulation."""
    config_label: str
    total_districts: int
    democratic_wins: int
    republican_wins: int
    other_wins: int
    district_results: List[DistrictResult]
    
    @property
    def democratic_percentage(self) -> float:
        """Percentage of districts won by Democrats."""
        return (self.democratic_wins / self.total_districts) * 100
    
    @property
    def republican_percentage(self) -> float:
        """Percentage of districts won by Republicans."""
        return (self.republican_wins / self.total_districts) * 100
    
    def get_candidate_win_counts(self) -> Dict[str, int]:
        """Get count of wins by candidate name."""
        candidate_counts = {}
        for result in self.district_results:
            candidate_name = result.winner_name
            candidate_counts[candidate_name] = candidate_counts.get(candidate_name, 0) + 1
        return candidate_counts


class CongressionalSimulation:
    """Simulates elections for all 435 congressional districts."""
    
    def __init__(self, config: Optional[UnitSimulationConfig] = None, 
                 gaussian_generator: Optional[GaussianGenerator] = None,
                 election_type: str = "primary"):
        """Initialize congressional simulation.
        
        Args:
            config: Simulation configuration
            gaussian_generator: Random number generator
            election_type: Type of election ("primary", "irv", "condorcet")
        """
        self.config = config or CongressionalSimulationConfigFactory.create_config(3)
        self.gaussian_generator = gaussian_generator
        self.election_type = election_type
        self.data_file = None  # Will be set when run_simulation is called
    
    def load_districts(self, csv_file: str) -> List[DistrictVotingRecord]:
        """Load district data from CSV file."""
        cook_data = CookPoliticalData(csv_file)
        return cook_data.load_districts()
    
    def simulate_district(self, district: DistrictVotingRecord) -> DistrictResult:
        """Simulate election for a single district."""
        # Create election process based on election type and state
        if self.election_type == "top-2":
            election_process = ActualCustomElection(state_abbr='CA', primary_skew=self.config.primary_skew, debug=False)
        elif self.election_type == "primary":
            election_process = ElectionWithPrimary(primary_skew=self.config.primary_skew, debug=False)
        elif self.election_type == "condorcet":
            election_process = CondorcetElection(debug=False)
        elif self.election_type == "irv":    # instant runoff
            election_process = InstantRunoffElection(debug=False)
        elif self.election_type == "custom":
            # Use state abbreviation directly from district.state
            election_process = ActualCustomElection(state_abbr=district.state, primary_skew=self.config.primary_skew, debug=False)
        else:
            raise ValueError(f"Unknown election type: {self.election_type}")
        
        # Generate election definition
        election_def = self.config.generate_definition(district, self.gaussian_generator)
        
        ballots = []
        for voter in election_def.population.voters:
            ballot = RCVBallot(voter, election_def.candidates, election_def.config, self.gaussian_generator)
            ballots.append(ballot)
        
        # Run election
        result = election_process.run(election_def.candidates, ballots)
        
        # Extract winner information
        winner = result.winner()
        ordered_results = result.ordered_results()
        
        # Calculate margin
        margin = 0.0
        if len(ordered_results) > 1:
            winner_votes = ordered_results[0].votes
            second_votes = ordered_results[1].votes
            margin = winner_votes - second_votes
        
        return DistrictResult(
            district=district.district,
            state=district.state,
            incumbent=district.incumbent,
            expected_lean=district.expected_lean,
            winner_name=winner.name,
            winner_party=winner.tag.short_name,
            winner_ideology=winner.ideology,
            voter_satisfaction=result.voter_satisfaction(),
            total_votes=result.n_votes,
            margin=margin
        )
    
    def _print_median_candidate_details(self, district: DistrictVotingRecord, 
                                      election_def: ElectionDefinition, 
                                      result: ElectionResult) -> None:
        """Print detailed information when a median candidate wins."""
        print(f"\n=== MEDIAN CANDIDATE WIN: {district.district} ===")
        print(f"District: {district.district} ({district.state})")
        print(f"Partisan Lean: {district.expected_lean:+.1f}")
        print(f"Incumbent: {district.incumbent}")
        
        # Get party centers
        dem_center = election_def.population.democrats.mean
        rep_center = election_def.population.republicans.mean
        print(f"Democratic Party Center: {dem_center:.2f}")
        print(f"Republican Party Center: {rep_center:.2f}")
        
        # Print all candidates with their ideology and vote counts
        print("\nAll Candidates:")
        for candidate_result in result.ordered_results:
            candidate = candidate_result.candidate
            winner_marker = " ← WINNER" if candidate_result == result.ordered_results[0] else ""
            print(f"  {candidate.name:4s} ({candidate.tag.short_name:3s}): "
                  f"Ideology={candidate.ideology:6.2f}, Votes={candidate_result.votes:6.1f}{winner_marker}")
        
        print(f"Total Votes: {result.n_votes:.1f}")
        print(f"Voter Satisfaction: {result.voter_satisfaction:.3f}")
        print("=" * 50)
    
    def _check_median_candidate_primaries(self, district: DistrictVotingRecord, 
                                        election_def: ElectionDefinition, 
                                        result: ElectionWithPrimaryResult) -> None:
        """Check if median candidates won in primaries and print detailed info."""
        # Check Democratic primary
        dem_winner = result.democratic_primary.winner()
        if dem_winner.name == 'D-V':
            self._print_median_candidate_primary_details(
                district, election_def, result.democratic_primary, "Democratic"
            )
        
        # Check Republican primary
        rep_winner = result.republican_primary.winner()
        if rep_winner.name == 'R-V':
            self._print_median_candidate_primary_details(
                district, election_def, result.republican_primary, "Republican"
            )
    
    def _print_median_candidate_primary_details(self, district: DistrictVotingRecord, 
                                              election_def: ElectionDefinition, 
                                              primary_result: ElectionResult, 
                                              party: str) -> None:
        """Print detailed information when a median candidate wins a primary."""
        print(f"\n=== MEDIAN CANDIDATE PRIMARY WIN: {district.district} ({party}) ===")
        print(f"District: {district.district} ({district.state})")
        print(f"Partisan Lean: {district.expected_lean:+.1f}")
        print(f"Incumbent: {district.incumbent}")
        
        # Get party centers
        dem_center = election_def.population.democrats.mean
        rep_center = election_def.population.republicans.mean
        print(f"Democratic Party Center: {dem_center:.2f}")
        print(f"Republican Party Center: {rep_center:.2f}")
        
        # Print all candidates in this primary with their ideology and vote counts
        print(f"\n{party} Primary Candidates:")
        for candidate_result in primary_result.ordered_results():
            candidate = candidate_result.candidate
            winner_marker = " ← WINNER" if candidate_result == primary_result.ordered_results()[0] else ""
            print(f"  {candidate.name:4s} ({candidate.tag.short_name:3s}): "
                  f"Ideology={candidate.ideology:6.2f}, Votes={candidate_result.votes:6.1f}{winner_marker}")
        
        print(f"Total Primary Votes: {primary_result.n_votes:.1f}")
        print(f"Primary Voter Satisfaction: {primary_result.voter_satisfaction():.3f}")
        print("=" * 50)
    
    def simulate_all_districts(self, districts: List[DistrictVotingRecord]) -> CongressionalSimulationResult:
        """Simulate elections for all districts."""
        district_results = []
        democratic_wins = 0
        republican_wins = 0
        other_wins = 0
        
        print(f"Simulating {len(districts)} districts...")
        
        for i, district in enumerate(districts):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(districts)} districts")
            
            result = self.simulate_district(district)
            district_results.append(result)
            
            # Count wins by party
            if result.winner_party == "Dem":
                democratic_wins += 1
            elif result.winner_party == "Rep":
                republican_wins += 1
            else:
                other_wins += 1
        
        return CongressionalSimulationResult(
            config_label=self.config.label,
            total_districts=len(districts),
            democratic_wins=democratic_wins,
            republican_wins=republican_wins,
            other_wins=other_wins,
            district_results=district_results
        )
    
    def run_simulation(self, csv_file: str) -> CongressionalSimulationResult:
        """Run complete simulation from CSV file."""
        self.data_file = csv_file  # Store for later use
        districts = self.load_districts(csv_file)
        return self.simulate_all_districts(districts)
    
    def save_results(self, result: CongressionalSimulationResult, filename: str) -> None:
        """Save simulation results to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, default=str)
    
    def print_summary(self, result: CongressionalSimulationResult) -> None:
        """Print summary of simulation results."""
        print("\n=== Congressional Simulation Results ===")
        print(f"Configuration: {result.config_label}")
        print(f"Total Districts: {result.total_districts}")
        print(f"Democratic Wins: {result.democratic_wins} ({result.democratic_percentage:.1f}%)")
        print(f"Republican Wins: {result.republican_wins} ({result.republican_percentage:.1f}%)")
        print(f"Other Wins: {result.other_wins}")
        
        # Calculate average voter satisfaction
        avg_satisfaction = sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results)
        print(f"Average Voter Satisfaction: {avg_satisfaction:.3f}")
        
        # Show candidate win counts
        candidate_counts = result.get_candidate_win_counts()
        print("\n=== Candidate Win Counts ===")
        # Sort by count (descending) then by name
        sorted_candidates = sorted(candidate_counts.items(), key=lambda x: (-x[1], x[0]))
        for candidate_name, count in sorted_candidates:
            print(f"{candidate_name}: {count}")
        
        # Show some interesting districts
        print("\n=== Sample Results ===")
        for i, dr in enumerate(result.district_results[:10]):
            print(f"{dr.district}: {dr.winner_party} {dr.winner_name} "
                  f"(Lean: {dr.expected_lean:+.1f}, Satisfaction: {dr.voter_satisfaction:.3f})")
