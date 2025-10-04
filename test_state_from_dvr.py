#!/usr/bin/env python3
"""
Test script for passing state from DistrictVotingRecord to ElectionDefinition.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.simulation_config import UnitSimulationConfig
from simulation_base.gaussian_generator import GaussianGenerator

def test_state_from_dvr():
    """Test that state is passed from DistrictVotingRecord to ElectionDefinition."""
    print("Testing state passing from DistrictVotingRecord...")
    
    # Create a DistrictVotingRecord with a specific state
    dvr = DistrictVotingRecord(
        district="CA-12",
        incumbent="Test Incumbent",
        expected_lean=-5.0,
        d_pct1=0.52,
        r_pct1=0.48,
        d_pct2=0.53,
        r_pct2=0.47
    )
    
    print(f"DistrictVotingRecord district: {dvr.district}")
    print(f"DistrictVotingRecord state: {dvr.state}")
    
    # Create a minimal UnitSimulationConfig
    # We need to create a minimal config for testing
    from simulation_base.simulation_config import PopulationConfiguration
    from simulation_base.candidate_generator import CandidateGenerator
    from simulation_base.election_config import ElectionConfig
    
    pop_config = PopulationConfiguration(
        partisanship=0.0,
        stddev=0.3,
        population_skew=0.0
    )
    
    from simulation_base.candidate_generator import PartisanCandidateGenerator
    
    candidate_generator = PartisanCandidateGenerator(
        n_party_candidates=2,
        spread=1.0,
        ideology_variance=0.5,
        quality_variance=0.2,
        primary_skew=0.1,
        median_variance=0.1
    )
    
    config = ElectionConfig(uncertainty=0.1)
    
    unit_config = UnitSimulationConfig(
        label="test",
        config=config,
        pop_config=pop_config,
        candidate_generator=candidate_generator,
        primary_skew=0.1,
        nvoters=100
    )
    
    # Create gaussian generator
    gaussian_generator = GaussianGenerator(seed=42)
    
    # Generate election definition
    try:
        election_def = unit_config.generate_definition(dvr, gaussian_generator)
        print(f"✓ Successfully created ElectionDefinition")
        print(f"  State: {election_def.state}")
        print(f"  Expected: CA")
        
        if election_def.state == "CA":
            print("✓ State correctly extracted from DistrictVotingRecord")
        else:
            print(f"✗ State mismatch: expected CA, got {election_def.state}")
            
    except Exception as e:
        print(f"✗ Error creating ElectionDefinition: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with a DistrictVotingRecord without state
    print("\nTesting with DistrictVotingRecord without state...")
    
    # Create a mock object that doesn't have a state attribute
    class MockDVR:
        def __init__(self):
            self.district = "Unknown"
            self.expected_lean = 0.0
            self.d_pct1 = 0.5
            self.r_pct1 = 0.5
            self.d_pct2 = 0.5
            self.r_pct2 = 0.5
    
    mock_dvr = MockDVR()
    
    try:
        election_def = unit_config.generate_definition(mock_dvr, gaussian_generator)
        print(f"✓ Successfully created ElectionDefinition with mock DVR")
        print(f"  State: {election_def.state}")
        print(f"  Expected: TX (default)")
        
        if election_def.state == "TX":
            print("✓ Default state TX correctly used")
        else:
            print(f"✗ State mismatch: expected TX, got {election_def.state}")
            
    except Exception as e:
        print(f"✗ Error creating ElectionDefinition with mock DVR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_state_from_dvr()
