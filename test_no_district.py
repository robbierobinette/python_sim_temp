#!/usr/bin/env python3
"""
Test script for ElectionDefinition without district_name.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator

def test_no_district():
    """Test that district_name is removed from ElectionDefinition."""
    print("Testing ElectionDefinition without district_name...")
    
    # Create minimal test data
    candidates = [
        Candidate("Dem-A", DEMOCRATS, -1.0, 0.8),
        Candidate("Rep-A", REPUBLICANS, 1.0, 0.8),
    ]
    
    population = CombinedPopulation(
        populations=[PopulationGroup(DEMOCRATS, -1.0, 0.3, 100.0)],
        desired_samples=100
    )
    
    config = ElectionConfig(uncertainty=0.1)
    gaussian_generator = GaussianGenerator(seed=42)
    
    # Test 1: Valid ElectionDefinition with only state
    print("Test 1: Valid ElectionDefinition with state")
    try:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="TX"
        )
        print(f"  ✓ Success: state = {election_def.state}")
        print(f"  ✓ Has district_name attribute: {hasattr(election_def, 'district_name')}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: Try to pass district_name (should fail)
    print("Test 2: Try to pass district_name (should fail)")
    try:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="TX",
            district_name="TX-01"
        )
        print(f"  ✗ Unexpected success: state = {election_def.state}")
    except TypeError as e:
        print(f"  ✓ Expected error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_no_district()
