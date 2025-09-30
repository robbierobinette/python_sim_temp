#!/usr/bin/env python3
"""
Main program to run congressional election simulation.

This program simulates elections for all 435 congressional districts using
ranked choice voting (instant runoff) based on the Cook Political Report data.
"""

import argparse
import sys
import os
from congressional_simulation import CongressionalSimulation
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
        help="Number of candidates: per party for partisan/normal-partisan, total for random/condorcet (default: 3)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--election-type", 
        choices=["primary", "irv", "condorcet"],
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
    parser.add_argument(
        "--nvoters", 
        type=int,
        default=1000,
        help="Number of voters per district (default: 1000)"
    )
    parser.add_argument(
        "--partisan-shift", 
        type=float,
        default=0.01,
        help="Partisan shift of the population (default: 0.01), meaning a shift of .01 sigma every point of partisan lean"
    )
    parser.add_argument(
        "--uncertainty", 
        type=float,
        default=0.1,
        help="Voter uncertainty factor (default: 0.0)"
    )
    parser.add_argument(
        "--primary-skew", 
        type=float,
        default=0.25,
        help="Primary election skew factor (default: 0.5)"
    )
    parser.add_argument(
        "--candidate-generator", 
        choices=["partisan", "condorcet", "random", "normal-partisan"],
        default="partisan",
        help="Type of candidate generator to use (default: partisan)"
    )
    parser.add_argument(
        "--condorcet-variance", 
        type=float,
        default=0.1,
        help="Ideology variance for Condorcet candidates (default: 0.5)"
    )
    parser.add_argument(
        "--ideology-variance", 
        type=float,
        default=0.10,
        help="Ideology variance for candidates (default: 0.20)"
    )
    parser.add_argument(
        "--spread", 
        type=float,
        default=0.4,
        help="Spread for partisan candidate generator (default: 0.4)"
    )
    parser.add_argument(
        "--quality-variance", 
        type=float,
        default=0.0,
        help="Quality variance for candidate generation (default: 0.0)"
    )
    parser.add_argument(
        "--adjust-for-centrists", 
        choices=["dominant", "both", "none"],
        default="dominant",
        help="Adjust candidates for centrist constraints: 'dominant' (default), 'both', or 'none'"
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
    config_params = {
        'candidates': args.candidates,
        'gaussian_generator': gaussian_generator,
        'nvoters': args.nvoters,
        'uncertainty': args.uncertainty,
        'primary_skew': args.primary_skew,
        'candidate_generator_type': args.candidate_generator,
        'condorcet_variance': args.condorcet_variance,
        'election_type': args.election_type,
        'ideology_variance': args.ideology_variance,
        'spread': args.spread,
        'quality_variance': args.quality_variance,
        'partisan_shift': args.partisan_shift,
        'adjust_for_centrists': args.adjust_for_centrists
    }
    config = CongressionalSimulationConfigFactory.create_config(config_params)
    
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
        print("\n=== Additional Statistics ===")
        
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
        if args.plot or args.histogram_only or args.plot_dir != "plots":
            try:
                # Determine if we should save files and show plots
                save_files = args.plot_dir != "plots"  # Only save if plot-dir was explicitly specified
                show_plots = args.plot  # Only show if --plot was specified
                
                if save_files:
                    # Create plot directory if it doesn't exist
                    os.makedirs(args.plot_dir, exist_ok=True)
                
                if args.histogram_only:
                    print("\nGenerating winner ideology histogram...")
                    save_path = os.path.join(args.plot_dir, "winner_ideology_histogram.png") if save_files else None
                    plot_winner_ideology_histogram(result, 
                                                 save_path=save_path,
                                                 show_plot=show_plots)
                else:
                    print("\nGenerating all visualizations...")
                    output_dir = args.plot_dir if save_files else None
                    create_all_visualizations(result, 
                                            output_dir=output_dir,
                                            show_plots=show_plots)
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
