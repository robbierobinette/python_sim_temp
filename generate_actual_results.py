#!/usr/bin/env python3
"""
Generate results-actual.json from HSall_members.csv data for Congress 119.

This script reads the actual congressional data and generates a JSON file
in the same format as the simulation results. It:

1. Reads HSall_members.csv and filters for Congress 119 House members
2. Maps nominate_dim1 values to ideology scale (multiplies by 3)
3. Creates district populations using the same method as simulations
4. Calculates voter satisfaction for each member based on their ideology
5. Generates JSON output with all required fields (district, party, ideology, etc.)

Usage:
    python generate_actual_results.py

Output:
    results-actual.json - JSON file with actual congressional results
"""

import csv
import json
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Import simulation modules
from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.unit_population import UnitPopulation
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate import Candidate
from simulation_base.voter import Voter


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


def parse_hsall_members(filename: str) -> List[Dict]:
    """Parse HSall_members.csv and return list of member records."""
    members = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only process House members from Congress 119 with valid nominate scores
            # Exclude non-voting delegates (territories like AS, GU, etc.)
            if (row['congress'] == '119' and 
                row['chamber'] == 'House' and 
                row['nominate_dim1'] != '' and
                row['state_abbrev'] not in ['AS', 'GU', 'MP', 'VI', 'DC']):  # Exclude non-voting delegates
                members.append(row)
    
    return members


def map_party_code(party_code: str) -> str:
    """Map party code to party name."""
    party_map = {
        '100': 'Dem',  # Democratic
        '200': 'Rep',  # Republican
        '328': 'Ind',  # Independent
        '329': 'Ind',  # Independent
    }
    return party_map.get(party_code, 'Other')


def create_district_voting_record(member: Dict) -> DistrictVotingRecord:
    """Create a DistrictVotingRecord from member data."""
    state_abbrev = member['state_abbrev']
    district_code = member['district_code']
    
    # Create district identifier
    if district_code == '0':
        district = f"{state_abbrev}-AL"  # At-large
    else:
        district = f"{state_abbrev}-{district_code.zfill(2)}"
    
    # Use member name as incumbent
    incumbent = member['bioname']
    
    # Estimate expected lean based on member's ideology
    # More conservative members (positive nominate_dim1) suggest more Republican-leaning districts
    nominate_dim1 = float(member['nominate_dim1'])
    expected_lean = nominate_dim1 * 30.0  # Scale to reasonable lean range
    
    # Estimate party percentages based on lean
    lean_factor = expected_lean / 100.0
    d_pct = 50.0 - lean_factor * 25.0  # Democratic percentage
    r_pct = 50.0 + lean_factor * 25.0   # Republican percentage
    
    return DistrictVotingRecord(
        district=district,
        incumbent=incumbent,
        expected_lean=expected_lean,
        d_pct1=max(10.0, min(90.0, d_pct)),  # Clamp between 10% and 90%
        r_pct1=max(10.0, min(90.0, r_pct)),
        d_pct2=max(10.0, min(90.0, d_pct)),
        r_pct2=max(10.0, min(90.0, r_pct))
    )


def calculate_voter_satisfaction(member: Dict, population: CombinedPopulation) -> float:
    """Calculate voter satisfaction for a member based on their ideology and district population."""
    # Get member ideology (nominate_dim1 scaled by 3)
    nominate_dim1 = float(member['nominate_dim1'])
    member_ideology = nominate_dim1 * 3.0  # Scale from [-1,1] to [-3,3]
    
    # Create a candidate representing the actual member
    party_code = member['party_code']
    party_tag = DEMOCRATS if party_code == '100' else REPUBLICANS if party_code == '200' else INDEPENDENTS
    
    candidate = Candidate(
        name=member['bioname'],
        tag=party_tag,
        ideology=member_ideology,
        quality=0.0,  # No quality adjustment for actual members
        incumbent=True
    )
    
    # Calculate satisfaction based on how well the member represents the district
    voters = population.voters
    if not voters:
        return 0.5  # Default satisfaction if no voters
    
    # Count voters on each side of the member's ideology
    left_voter_count = sum(1 for v in voters if v.ideology < member_ideology)
    total_voters = len(voters)
    
    # Calculate satisfaction: 1 - |(2 * left_count / total) - 1|
    # This measures how well the member represents the median voter
    satisfaction = 1 - abs((2.0 * left_voter_count / total_voters) - 1)
    
    return satisfaction


def generate_actual_results(members: List[Dict]) -> CongressionalSimulationResult:
    """Generate simulation results from actual congressional data."""
    district_results = []
    democratic_wins = 0
    republican_wins = 0
    other_wins = 0
    
    for member in members:
        # Create district voting record
        dvr = create_district_voting_record(member)
        
        # Create population for this district
        population = UnitPopulation.create(dvr, n_voters=1000)
        
        # Calculate voter satisfaction
        satisfaction = calculate_voter_satisfaction(member, population)
        
        # Map party code to party name
        party_code = member['party_code']
        winner_party = map_party_code(party_code)
        
        # Count wins by party
        if winner_party == 'Dem':
            democratic_wins += 1
        elif winner_party == 'Rep':
            republican_wins += 1
        else:
            other_wins += 1
        
        # Create district result
        nominate_dim1 = float(member['nominate_dim1'])
        member_ideology = nominate_dim1 * 3.0
        
        district_result = DistrictResult(
            district=dvr.district,
            state=dvr.state,
            incumbent=member['bioname'],
            expected_lean=dvr.expected_lean,
            winner_name=member['bioname'],
            winner_party=winner_party,
            winner_ideology=member_ideology,
            voter_satisfaction=satisfaction,
            total_votes=10000.0,  # Default total votes
            margin=1000.0  # Default margin
        )
        
        district_results.append(district_result)
    
    return CongressionalSimulationResult(
        config_label="actualCongress119",
        total_districts=len(district_results),
        democratic_wins=democratic_wins,
        republican_wins=republican_wins,
        other_wins=other_wins,
        district_results=district_results
    )


def main():
    """Main function to generate results-actual.json."""
    print("Generating results-actual.json from HSall_members.csv...")
    
    # Parse the CSV file
    try:
        members = parse_hsall_members('HSall_members.csv')
        print(f"Found {len(members)} House members from Congress 119")
    except FileNotFoundError:
        print("Error: HSall_members.csv not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        sys.exit(1)
    
    # Generate results
    try:
        results = generate_actual_results(members)
        
        # Convert to dictionary for JSON serialization
        results_dict = asdict(results)
        
        # Write to JSON file
        with open('results-actual.json', 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"Results written to results-actual.json")
        print(f"Total districts: {results.total_districts}")
        print(f"Democratic wins: {results.democratic_wins}")
        print(f"Republican wins: {results.republican_wins}")
        print(f"Other wins: {results.other_wins}")
        
        # Calculate and display some statistics
        avg_satisfaction = sum(dr.voter_satisfaction for dr in results.district_results) / len(results.district_results)
        print(f"Average voter satisfaction: {avg_satisfaction:.3f}")
        
    except Exception as e:
        print(f"Error generating results: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
