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
import argparse
import traceback
from typing import List, Dict
from dataclasses import dataclass, asdict

# Import simulation modules
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.unit_population import UnitPopulation
from simulation_base.combined_population import CombinedPopulation
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
    nominate_dim1: float  # DW-NOMINATE first dimension score
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



def calculate_voter_satisfaction(member: Dict, population: CombinedPopulation) -> float:
    """Calculate voter satisfaction for a member based on their ideology and district population."""
    # Get member ideology (nominate_dim1 scaled by 3)
    nominate_dim1 = float(member['nominate_dim1'])
    member_ideology = nominate_dim1 * 2.0  # Scale from [-1,1] to [-2.0, 2.0]

    # Calculate satisfaction based on how well the member represents the district
    voters = population.voters
    
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

    # Load districts from CookPoliticalData.csv
    cook_data = CookPoliticalData("CookPoliticalData.csv")
    dvr_map = cook_data.get_districts_dict()
    
    for member in members:
        # Format district name to match the format used in load_districts
        state_abbrev = member['state_abbrev']
        district_code = member['district_code']
        
        # Format district identifier (e.g., "CA-15" or "AK-01" for at-large)
        # Convert district_code to string if it's not already
        district_code_str = str(district_code)
        
        if district_code_str == '0':
            district_name = f"{state_abbrev}-01"  # At-large districts are represented as 01
        else:
            district_num = int(district_code_str)
            district_name = f"{state_abbrev}-{district_num:02d}"
        
        # Get the district voting record
        if district_name not in dvr_map:
            print(f"Warning: District {district_name} not found in Cook Political Data, skipping {member['bioname']}")
            continue
            
        dvr = dvr_map[district_name]
        gaussian_generator = GaussianGenerator()
        
        # Create population for this district
        population = UnitPopulation.create(dvr, n_voters=1000, gaussian_generator=gaussian_generator)
        
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
        member_ideology = nominate_dim1 * 2.0  # Scale from [-1,1] to [-2.5, 2.5]
        
        district_result = DistrictResult(
            district=dvr.district,
            state=dvr.state,
            incumbent=member['bioname'],
            expected_lean=dvr.expected_lean,
            winner_name=member['bioname'],
            winner_party=winner_party,
            winner_ideology=member_ideology,
            nominate_dim1=nominate_dim1,
            voter_satisfaction=satisfaction,
            total_votes=10000.0,  # Default total votes
            margin=1000.0  # Default margin
        )
        
        district_results.append(district_result)
    
    return CongressionalSimulationResult(
        config_label="Congress119",
        total_districts=len(district_results),
        democratic_wins=democratic_wins,
        republican_wins=republican_wins,
        other_wins=other_wins,
        district_results=district_results
    )


def main():
    """Main function to generate results-current.json."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate results from HSall_members.csv')
    parser.add_argument(
        '-o', '--output',
        default='./results-current.json',
        help='Output file path (default: ./results-current.json)'
    )
    args = parser.parse_args()
    
    print(f"Generating {args.output} from HSall_members.csv...")
    
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
        with open(args.output, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"Results written to {args.output}")
        print(f"Total districts: {results.total_districts}")
        print(f"Democratic wins: {results.democratic_wins}")
        print(f"Republican wins: {results.republican_wins}")
        print(f"Other wins: {results.other_wins}")
        
        # Calculate and display some statistics
        avg_satisfaction = sum(dr.voter_satisfaction for dr in results.district_results) / len(results.district_results)
        print(f"Average voter satisfaction: {avg_satisfaction:.3f}")
        
    except Exception as e:
        print(f"Error generating results: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
