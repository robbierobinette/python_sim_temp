#!/usr/bin/env python3
"""
Test script for the SmartPrimaryElection.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.smart_primary_election import SmartPrimaryElection
from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator

def test_smart_primary():
    """Test the SmartPrimaryElection with different states."""
    print("Testing SmartPrimaryElection...")
    
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
    
    # Test different states
    test_states = ["CA", "TX", "AK", "LA", "ME", "XX"]  # XX is invalid state
    
    for state in test_states:
        print(f"\n=== Testing state: {state} ===")
        
        # Create election definition
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state=state
        )
        
        # Create smart primary election
        smart_primary = SmartPrimaryElection(debug=True)
        
        try:
            # Run the election
            result = smart_primary.run(election_def)
            
            print(f"✓ Successfully ran election for {state}")
            print(f"  Winner: {result.winner().name}")
            print(f"  Voter satisfaction: {result.voter_satisfaction():.3f}")
            print(f"  Final candidates: {[c.candidate.name for c in result.ordered_results()]}")
            
        except Exception as e:
            print(f"✗ Error running election for {state}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_smart_primary()
