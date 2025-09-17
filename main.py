#!/usr/bin/env python3
"""
Main program to run congressional election simulation.

This program simulates elections for all 435 congressional districts using
ranked choice voting (instant runoff) based on the Cook Political Report data.
"""

import argparse
import sys
import os
from typing import Optional
from congressional_simulation import CongressionalSimulation, CongressionalSimulationResult
from simulation_base.simulation_config import CongressionalSimulationConfigFactory
from simulation_base.gaussian_generator import GaussianGenerator, set_seed
from visualization import create_all_visualizations, plot_winner_ideology_histogram


def main():
    """Main entry point for the simulation."""
    parser = argparse.ArgumentParser(
        description="Simulate congressional elections using ranked choice voting"
    )
    parser.add_argument(
        "--data-file", 
        default="CookPoliticalData.csv",
        help="Path to CSV file with district data (default: CookPoliticalData.csv)"
    )
    parser.add_argument(
        "--output", 
        default="simulation_results.json",
        help="Output file for results (default: simulation_results.json)"
    )
    parser.add_argument(
        "--seed", 
        type=int,
        help="Random seed for reproducible results"
    )
    parser.add_argument(
        "--candidates", 
        type=int,
        default=3,
        help="Number of candidates per party (default: 3)"
    )
    parser.add_argument(
        "--voters", 
        type=int,
        default=1000,
        help="Number of voters per district (default: 1000)"
    )
    parser.add_argument(
        "--uncertainty", 
        type=float,
        default=0.5,
        help="Amount of voter uncertainty (default: 0.5)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--election-type", 
        choices=["primary", "instant_runoff", "head_to_head"],
        default="primary",
        help="Type of election to run (default: primary)"
    )
    parser.add_argument(
        "--plot", 
        action="store_true",
        help="Generate and display plots"
    )
    parser.add_argument(
        "--plot-dir", 
        default="plots",
        help="Directory to save plots (default: plots)"
    )
    parser.add_argument(
        "--histogram-only", 
        action="store_true",
        help="Generate only the winner ideology histogram"
    )
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not os.path.exists(args.data_file):
        print(f"Error: Data file '{args.data_file}' not found")
        sys.exit(1)
    
    # Set random seed if provided
    if args.seed is not None:
        set_seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Create simulation configuration
    gaussian_generator = GaussianGenerator(args.seed)
    config = CongressionalSimulationConfigFactory.create_config(
        args.candidates, gaussian_generator, args.voters, args.uncertainty
    )
    
    if args.verbose:
        print(f"Configuration: {config.describe()}")
    
    # Create and run simulation
    simulation = CongressionalSimulation(config, gaussian_generator, args.election_type)
    
    try:
        print(f"Loading district data from {args.data_file}...")
        result = simulation.run_simulation(args.data_file)
        
        # Print summary
        simulation.print_summary(result)
        
        # Save results
        simulation.save_results(result, args.output)
        print(f"\nResults saved to {args.output}")
        
        # Print some statistics
        print(f"\n=== Additional Statistics ===")
        
        # Party distribution
        dem_districts = [dr for dr in result.district_results if dr.winner_party == "Dem"]
        rep_districts = [dr for dr in result.district_results if dr.winner_party == "Rep"]
        
        if dem_districts:
            avg_dem_lean = sum(dr.expected_lean for dr in dem_districts) / len(dem_districts)
            print(f"Average lean of Democratic districts: {avg_dem_lean:.1f}")
        
        if rep_districts:
            avg_rep_lean = sum(dr.expected_lean for dr in rep_districts) / len(rep_districts)
            print(f"Average lean of Republican districts: {avg_rep_lean:.1f}")
        
        # Ideology distribution
        avg_ideology = sum(dr.winner_ideology for dr in result.district_results) / len(result.district_results)
        print(f"Average winner ideology: {avg_ideology:.2f}")
        
        # Satisfaction by party
        dem_satisfaction = sum(dr.voter_satisfaction for dr in dem_districts) / len(dem_districts) if dem_districts else 0
        rep_satisfaction = sum(dr.voter_satisfaction for dr in rep_districts) / len(rep_districts) if rep_districts else 0
        print(f"Average satisfaction in Democratic districts: {dem_satisfaction:.3f}")
        print(f"Average satisfaction in Republican districts: {rep_satisfaction:.3f}")
        
        # Generate visualizations if requested
        if args.plot or args.histogram_only:
            try:
                # Create plot directory if it doesn't exist
                os.makedirs(args.plot_dir, exist_ok=True)
                
                if args.histogram_only:
                    print(f"\nGenerating winner ideology histogram...")
                    plot_winner_ideology_histogram(result, 
                                                 save_path=os.path.join(args.plot_dir, "winner_ideology_histogram.png"),
                                                 show_plot=args.plot)
                else:
                    print(f"\nGenerating all visualizations...")
                    create_all_visualizations(result, 
                                            output_dir=args.plot_dir,
                                            show_plots=args.plot)
            except ImportError as e:
                print(f"Warning: Could not generate plots - {e}")
                print("Make sure matplotlib and numpy are installed: pip install matplotlib numpy")
            except Exception as e:
                print(f"Error generating plots: {e}")
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
