#!/usr/bin/env python3
"""
Test script for the TopNPrimary election process.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.topn_primary import TopNPrimary
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator

def test_top2_primary():
    """Test the top-2 primary election process."""
    print("Testing TopNPrimary...")
    
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
        gaussian_generator=gaussian_generator,
        state="Test"
    )
    
    print(f"Total voters: {len(population.voters)}")
    print(f"Democratic voters: {len([v for v in population.voters if v.party.tag == DEMOCRATS])}")
    print(f"Republican voters: {len([v for v in population.voters if v.party.tag == REPUBLICANS])}")
    print(f"Independent voters: {len([v for v in population.voters if v.party.tag == INDEPENDENTS])}")
    print()
    
    # Test 1: Top-2 primary
    print("=== Test 1: Top-2 Primary ===")
    top2_primary = TopNPrimary(n=2, debug=True)
    
    result = top2_primary.run(election_def)
    
    print(f"Top 2 candidates: {[c.name for c in result.topn_candidates]}")
    print(f"Winner: {result.winner().name}")
    print()
    
    # Test 1b: Top-4 primary
    print("=== Test 1b: Top-4 Primary ===")
    top4_primary = TopNPrimary(n=4, debug=True)
    
    result4 = top4_primary.run(election_def)
    
    print(f"Top 4 candidates: {[c.name for c in result4.topn_candidates]}")
    print(f"Winner: {result4.winner().name}")
    print()
    
    # Test 2: Use in composable election
    print("=== Test 2: Top-2 Primary + IRV General Election ===")
    from simulation_base.composable_election import ComposableElection
    
    general_process = InstantRunoffElection(debug=True)
    composable_election = ComposableElection(top2_primary, general_process, debug=True)
    
    final_result = composable_election.run(election_def)
    
    print(f"Final election winner: {final_result.winner().name}")
    print(f"Voter satisfaction: {final_result.voter_satisfaction():.3f}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_top2_primary()
