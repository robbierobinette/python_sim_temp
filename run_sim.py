#!/usr/bin/env python3
"""
Main program to run congressional election simulation.

"""

import sys
from simulation_base.simulation_runner import parse_simulation_args, setup_simulation, run_simulation
from visualization import create_all_visualizations, plot_winner_ideology_histogram


def main():
    """Main entry point for the simulation."""
    # Parse arguments using shared runner
    parser = parse_simulation_args("Simulate congressional elections using ranked choice voting")
    args = parser.parse_args()
    
    # Setup simulation using shared runner
    config, gaussian_generator = setup_simulation(args)
    
    # Run simulation using shared runner
    simulation, result = run_simulation(
        config, gaussian_generator, args.data_file, args.election_type, args.verbose
    )
    
    # Print summary
    simulation.print_summary(result)
    
    # Save results
    simulation.save_results(result, args.output)
    print(f"\nResults saved to {args.output}")
    
      
    # Ideology distribution
    avg_satisfaction = sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results)
    print(f"Average voter satisfaction: {avg_satisfaction:.2f}")
    
    # Median candidate wins
    median_wins = sum(1 for dr in result.district_results if dr.winner_name.startswith("C-"))
    median_percentage = (median_wins / len(result.district_results)) * 100
    print(f"Median candidate wins: {median_wins}/{len(result.district_results)} ({median_percentage:.1f}%)")
    
    
    # Generate visualizations if requested
    if args.plot or args.histogram_only or args.plot_dir != "plots":
        try:
            # Determine if we should save files and show plots
            save_files = args.plot_dir != "plots"  # Only save if plot-dir was explicitly specified
            show_plots = args.plot  # Only show if --plot was specified
            
            if save_files:
                # Create plot directory if it doesn't exist
                import os
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


if __name__ == "__main__":
    main()
