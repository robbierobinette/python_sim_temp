#!/usr/bin/env python3
"""
Test script to demonstrate the congressional simulation functionality.
"""

from congressional_simulation import CongressionalSimulation
from simulation_base.simulation_config import CongressionalSimulationConfigFactory
from simulation_base.gaussian_generator import GaussianGenerator, set_seed
from visualization import plot_winner_ideology_histogram, create_all_visualizations


def test_single_district():
    """Test simulation of a single district."""
    print("=== Testing Single District Simulation ===")
    
    # Set seed for reproducibility
    set_seed(123)
    gaussian_generator = GaussianGenerator(123)
    
    # Create simulation config
    config = CongressionalSimulationConfigFactory.create_config(3, gaussian_generator)
    simulation = CongressionalSimulation(config, gaussian_generator)
    
    # Load districts
    districts = simulation.load_districts("CookPoliticalData.csv")
    
    # Test a few specific districts
    test_districts = ["Alabama-1", "California-14", "Texas-1"]
    
    for district_name in test_districts:
        district = next((d for d in districts if d.district == district_name), None)
        if district:
            print(f"\nTesting district: {district_name}")
            print(f"  Expected lean: {district.expected_lean}")
            print(f"  Incumbent: {district.incumbent}")
            
            result = simulation.simulate_district(district)
            print(f"  Winner: {result.winner_name} ({result.winner_party})")
            print(f"  Winner ideology: {result.winner_ideology:.2f}")
            print(f"  Voter satisfaction: {result.voter_satisfaction:.3f}")
            print(f"  Margin: {result.margin:.1f}")


def test_small_simulation():
    """Test simulation of a small subset of districts."""
    print("\n=== Testing Small Simulation ===")
    
    # Set seed for reproducibility
    set_seed(456)
    gaussian_generator = GaussianGenerator(456)
    
    # Create simulation
    config = CongressionalSimulationConfigFactory.create_config(3, gaussian_generator)
    simulation = CongressionalSimulation(config, gaussian_generator)
    
    # Load districts
    districts = simulation.load_districts("CookPoliticalData.csv")
    
    # Test with first 10 districts
    test_districts = districts[:10]
    print(f"Simulating {len(test_districts)} districts...")
    
    result = simulation.simulate_all_districts(test_districts)
    
    print(f"Results:")
    print(f"  Democratic wins: {result.democratic_wins}")
    print(f"  Republican wins: {result.republican_wins}")
    print(f"  Other wins: {result.other_wins}")
    print(f"  Average satisfaction: {sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results):.3f}")


def test_different_candidate_counts():
    """Test different numbers of candidates per party."""
    print("\n=== Testing Different Candidate Counts ===")
    
    set_seed(789)
    gaussian_generator = GaussianGenerator(789)
    
    # Load districts
    simulation = CongressionalSimulation(gaussian_generator=gaussian_generator)
    districts = simulation.load_districts("CookPoliticalData.csv")
    test_districts = districts[:5]  # Test with 5 districts
    
    candidate_counts = [2, 3, 5]
    
    for n_candidates in candidate_counts:
        print(f"\n{n_candidates} candidates per party:")
        
        config = CongressionalSimulationConfigFactory.create_config(n_candidates, gaussian_generator)
        simulation.config = config
        result = simulation.simulate_all_districts(test_districts)
        
        print(f"  Democratic wins: {result.democratic_wins}")
        print(f"  Republican wins: {result.republican_wins}")
        print(f"  Average satisfaction: {sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results):.3f}")


def test_visualizations():
    """Test visualization functionality."""
    print("\n=== Testing Visualizations ===")
    
    set_seed(999)
    gaussian_generator = GaussianGenerator(999)
    
    # Create simulation
    config = CongressionalSimulationConfigFactory.create_config(3, gaussian_generator)
    simulation = CongressionalSimulation(config, gaussian_generator)
    
    # Load districts
    districts = simulation.load_districts("CookPoliticalData.csv")
    
    # Test with first 20 districts
    test_districts = districts[:20]
    print(f"Simulating {len(test_districts)} districts for visualization test...")
    
    result = simulation.simulate_all_districts(test_districts)
    
    try:
        # Test histogram generation
        print("Generating winner ideology histogram...")
        plot_winner_ideology_histogram(result, 
                                     save_path="test_plots/test_histogram.png",
                                     show_plot=False)
        print("✓ Histogram generated successfully")
        
        # Test all visualizations
        print("Generating all visualizations...")
        create_all_visualizations(result, 
                                output_dir="test_plots",
                                show_plots=False)
        print("✓ All visualizations generated successfully")
        
    except ImportError as e:
        print(f"⚠ Visualization test skipped - {e}")
        print("Make sure matplotlib and numpy are installed: pip install matplotlib numpy")
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")


if __name__ == "__main__":
    test_single_district()
    test_small_simulation()
    test_different_candidate_counts()
    test_visualizations()
    print("\n=== All tests completed successfully! ===")
