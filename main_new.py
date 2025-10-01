#!/usr/bin/env python3
"""
Main program to run congressional election simulation.

This program simulates elections for all 435 congressional districts using
ranked choice voting (instant runoff) based on the Cook Political Report data.
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
    
    if args.verbose:
        print(f"Simulation completed: {result.total_districts} districts")
    
    # Print results
    print(f"\n=== Congressional Simulation Results ===")
    print(f"Configuration: {result.config_label}")
    print(f"Total Districts: {result.total_districts}")
    print(f"Democratic Wins: {result.democratic_wins} ({result.democratic_percentage:.1f}%)")
    print(f"Republican Wins: {result.republican_wins} ({result.republican_percentage:.1f}%)")
    print(f"Other Wins: {result.other_wins}")
    print(f"Average Voter Satisfaction: {sum(dr.voter_satisfaction for dr in result.district_results) / len(result.district_results):.3f}")
    
    # Print candidate win counts
    candidate_counts = result.get_candidate_win_counts()
    print(f"\n=== Candidate Win Counts ===")
    for candidate, count in sorted(candidate_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{candidate}: {count}")
    
    # Print sample results
    print(f"\n=== Sample Results ===")
    for i, dr in enumerate(result.district_results[:10]):
        print(f"{dr.district}: {dr.winner_party} {dr.winner_name} (Lean: {dr.expected_lean:+.1f}, Satisfaction: {dr.voter_satisfaction:.3f})")
    
    # Save results
    simulation.save_results(result, args.output)
    print(f"\nResults saved to {args.output}")
    
    # Print some statistics
    print("\n=== Additional Statistics ===")
    
    # Party distribution
    dem_districts = [dr for dr in result.district_results if dr.winner_party == "Dem"]
    rep_districts = [dr for dr in result.district_results if dr.winner_party == "Rep"]
    
    if dem_districts:
        avg_lean_dem = sum(dr.expected_lean for dr in dem_districts) / len(dem_districts)
        avg_satisfaction_dem = sum(dr.voter_satisfaction for dr in dem_districts) / len(dem_districts)
        print(f"Average lean of Democratic districts: {avg_lean_dem:.1f}")
        print(f"Average satisfaction in Democratic districts: {avg_satisfaction_dem:.3f}")
    
    if rep_districts:
        avg_lean_rep = sum(dr.expected_lean for dr in rep_districts) / len(rep_districts)
        avg_satisfaction_rep = sum(dr.voter_satisfaction for dr in rep_districts) / len(rep_districts)
        print(f"Average lean of Republican districts: {avg_lean_rep:.1f}")
        print(f"Average satisfaction in Republican districts: {avg_satisfaction_rep:.3f}")
    
    # Overall statistics
    avg_winner_ideology = sum(dr.winner_ideology for dr in result.district_results) / len(result.district_results)
    print(f"Average winner ideology: {avg_winner_ideology:.3f}")
    
    # Generate plots if requested
    if args.plot:
        print(f"\nGenerating plots...")
        try:
            if args.histogram_only:
                plot_winner_ideology_histogram(result, save_path=f"{args.plot_dir}/winner_ideology_histogram.png", show_plot=False)
            else:
                create_all_visualizations(result, save_dir=args.plot_dir, show_plots=False)
            print(f"Plots saved to {args.plot_dir}/")
        except Exception as e:
            print(f"Error generating plots: {e}")


if __name__ == "__main__":
    main()
