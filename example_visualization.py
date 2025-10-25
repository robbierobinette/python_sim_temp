#!/usr/bin/env python3
"""
Example script demonstrating the visualization capabilities of the congressional simulation.
"""

import os
from congressional_simulation import CongressionalSimulation
from simulation_base.simulation_config import CongressionalSimulationConfigFactory
from simulation_base.gaussian_generator import GaussianGenerator
from visualization import create_all_visualizations, plot_winner_ideology_histogram


def main():
    """Run a small simulation and generate visualizations."""
    print("=== Congressional Election Simulation with Visualizations ===")
    
    # Set seed for reproducibility
    gaussian_generator = GaussianGenerator(12345)
    
    # Create simulation config
    config = CongressionalSimulationConfigFactory.create_config(3, gaussian_generator)
    simulation = CongressionalSimulation(config, gaussian_generator)
    
    # Load districts
    print("Loading district data...")
    districts = simulation.load_districts("CookPoliticalData.csv")
    
    # Run simulation on a subset of districts for faster execution
    print(f"Simulating elections for {len(districts)} districts...")
    result = simulation.simulate_all_districts(districts)
    
    # Print summary
    print("\n=== Results Summary ===")
    print(f"Total Districts: {result.total_districts}")
    print(f"Democratic Wins: {result.democratic_wins} ({result.democratic_percentage:.1f}%)")
    print(f"Republican Wins: {result.republican_wins} ({result.republican_percentage:.1f}%)")
    print(f"Other Wins: {result.other_wins}")
    
    # Calculate average voter satisfaction
    avg_satisfaction = sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results)
    print(f"Average Voter Satisfaction: {avg_satisfaction:.3f}")
    
    # Generate visualizations
    print("\n=== Generating Visualizations ===")
    
    # Create output directory
    output_dir = "example_plots"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Generate all visualizations
        create_all_visualizations(result, 
                                output_dir=output_dir,
                                show_plots=False)
        
        print(f"✓ All visualizations saved to {output_dir}/")
        print("  - winner_ideology_histogram.png")
        print("  - voter_satisfaction_histogram.png") 
        print("  - ideology_vs_satisfaction.png")
        print("  - party_wins_by_state.png")
        
        # Also generate just the histogram as an example
        print("\nGenerating individual histogram example...")
        plot_winner_ideology_histogram(result,
                                     save_path=os.path.join(output_dir, "example_histogram.png"),
                                     show_plot=False)
        print(f"✓ Example histogram saved to {output_dir}/example_histogram.png")
        
    except ImportError as e:
        print(f"⚠ Could not generate visualizations: {e}")
        print("Make sure matplotlib and numpy are installed:")
        print("  pip install matplotlib numpy")
    except Exception as e:
        print(f"✗ Error generating visualizations: {e}")
    
    print("\n=== Example completed! ===")
    print(f"Check the {output_dir}/ directory for generated plots.")


if __name__ == "__main__":
    main()
