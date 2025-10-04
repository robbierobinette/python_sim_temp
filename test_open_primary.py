#!/usr/bin/env python3
"""
Test script for the OpenPrimary election process.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.open_primary import OpenPrimary, OpenPrimaryConfig
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator

def test_open_primary():
    """Test the open primary election process."""
    print("Testing OpenPrimary...")
    
    # Create test candidates
    candidates = [
        Candidate("Dem-A", DEMOCRATS, -2.0, 0.8),
        Candidate("Dem-B", DEMOCRATS, -1.0, 0.7),
        Candidate("Rep-A", REPUBLICANS, 1.0, 0.7),
        Candidate("Rep-B", REPUBLICANS, 2.0, 0.8),
        Candidate("Ind-A", INDEPENDENTS, 0.0, 0.6),
    ]
    
    # Create test population
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.5,
        stddev=0.3,
        weight=100.0
    )
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.5,
        stddev=0.3,
        weight=100.0
    )
    ind_group = PopulationGroup(
        tag=INDEPENDENTS,
        mean=0.0,
        stddev=0.3,
        weight=50.0
    )
    
    population = CombinedPopulation(
        populations=[dem_group, rep_group, ind_group],
        desired_samples=250
    )
    
    # Create election config
    config = ElectionConfig(uncertainty=0.1)
    
    # Create gaussian generator
    gaussian_generator = GaussianGenerator(seed=42)
    
    # Create election definition
    election_def = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator
    )
    
    print(f"Total voters: {len(population.voters)}")
    print(f"Democratic voters: {len([v for v in population.voters if v.party.tag == DEMOCRATS])}")
    print(f"Republican voters: {len([v for v in population.voters if v.party.tag == REPUBLICANS])}")
    print(f"Independent voters: {len([v for v in population.voters if v.party.tag == INDEPENDENTS])}")
    print()
    
    # Test 1: Open primary without runoff
    print("=== Test 1: Open Primary WITHOUT Runoff ===")
    primary_config = OpenPrimaryConfig(use_runoff=False, partisan_crossover_rate=0.1, independent_split_bias=0.0)
    open_primary = OpenPrimary(config=primary_config, debug=True)
    
    result = open_primary.run(election_def)
    
    print(f"Democratic winner: {result.democratic_winner.name if result.democratic_winner else 'None'}")
    print(f"Republican winner: {result.republican_winner.name if result.republican_winner else 'None'}")
    print(f"Final candidates: {[c.name for c in result.final_candidates]}")
    
    # Show voter assignments
    print("\nVoter assignments:")
    for voter_type, assignments in result.voter_assignments.items():
        print(f"  {voter_type}: {len(assignments)} voters")
        # Count assignments
        from collections import Counter
        assignment_counts = Counter(assignments)
        for assignment, count in assignment_counts.items():
            print(f"    {assignment}: {count}")
    print()
    
    # Test 2: Open primary with runoff
    print("=== Test 2: Open Primary WITH Runoff ===")
    primary_config_with_runoff = OpenPrimaryConfig(use_runoff=True, partisan_crossover_rate=0.15, independent_split_bias=0.1)
    open_primary_with_runoff = OpenPrimary(config=primary_config_with_runoff, debug=True)
    
    result_with_runoff = open_primary_with_runoff.run(election_def)
    
    print(f"Democratic winner: {result_with_runoff.democratic_winner.name if result_with_runoff.democratic_winner else 'None'}")
    print(f"Republican winner: {result_with_runoff.republican_winner.name if result_with_runoff.republican_winner else 'None'}")
    print(f"Final candidates: {[c.name for c in result_with_runoff.final_candidates]}")
    print()
    
    # Test 3: Use in composable election
    print("=== Test 3: Open Primary + IRV General Election ===")
    from simulation_base.composable_election import ComposableElection
    
    general_process = InstantRunoffElection(debug=True)
    composable_election = ComposableElection(open_primary_with_runoff, general_process, debug=True)
    
    final_result = composable_election.run(election_def)
    
    print(f"Final election winner: {final_result.winner().name}")
    print(f"Voter satisfaction: {final_result.voter_satisfaction():.3f}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_open_primary()
