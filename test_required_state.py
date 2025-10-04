#!/usr/bin/env python3
"""
Test script for the required state parameter in ElectionDefinition.
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

def test_required_state():
    """Test that state is now required in ElectionDefinition."""
    print("Testing required state parameter...")
    
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
    
    # Test 1: Valid state provided
    print("Test 1: Valid state provided")
    try:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="TX",
            district_name="TX-01"
        )
        print(f"  ✓ Success: state = {election_def.state}, district = {election_def.district_name}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: State provided without district
    print("Test 2: State provided without district")
    try:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="CA"
        )
        print(f"  ✓ Success: state = {election_def.state}, district = '{election_def.district_name}'")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 3: Missing state (should fail)
    print("Test 3: Missing state (should fail)")
    try:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            district_name="TX-01"
        )
        print(f"  ✗ Unexpected success: state = {election_def.state}")
    except TypeError as e:
        print(f"  ✓ Expected error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_required_state()
