#!/usr/bin/env python3
"""
Test script for the simplified state extraction.
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

def test_simplified_state_extraction():
    """Test the simplified state extraction from XX-NN format."""
    print("Testing simplified state extraction...")
    
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
    
    # Test cases
    test_cases = [
        ("", "TX"),  # Empty district name -> default to TX
        ("TX-01", "TX"),  # Texas district
        ("CA-12", "CA"),  # California district
        ("NY-15", "NY"),  # New York district
        ("FL-27", "FL"),  # Florida district
        ("OH-16", "OH"),  # Ohio district
        ("WA-01", "WA"),  # Washington district
        ("Invalid", "TX"),  # Invalid format -> default to TX
        ("XX", "TX"),  # Too short -> default to TX
        ("XX-", "XX"),  # Valid format, returns XX
    ]
    
    print("Testing state extraction from XX-NN format:")
    for district_name, expected_state in test_cases:
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            district_name=district_name
        )
        
        actual_state = election_def.state
        status = "✓" if actual_state == expected_state else "✗"
        print(f"  {status} '{district_name}' -> {actual_state} (expected: {expected_state})")
        
        if actual_state != expected_state:
            print(f"    ERROR: Expected {expected_state}, got {actual_state}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_simplified_state_extraction()
