#!/usr/bin/env python3
"""
Test script for the ElectionDefinition state extraction.
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

def test_election_definition_state():
    """Test the state extraction from district names."""
    print("Testing ElectionDefinition state extraction...")
    
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
        ("New York-15", "NY"),  # Full state name
        ("California District 5", "CA"),  # State name with "District"
        ("Texas-03", "TX"),  # Full state name with dash
        ("FL-27", "FL"),  # Florida district
        ("Pennsylvania-08", "PA"),  # Pennsylvania district
        ("Invalid District", "TX"),  # No valid state -> default to TX
        ("OH-16", "OH"),  # Ohio district
        ("Washington-01", "WA"),  # Washington district
    ]
    
    print("Testing state extraction from district names:")
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
    test_election_definition_state()
