#!/usr/bin/env python3
"""
Toxicity tests for election simulations.

This script tests the effects of toxic political tactics on election outcomes.
It runs two phases:
1. Base election → test if losing candidates could win with toxic tactics
2. Toxic base election → test if losing candidates could win by rejecting toxic tactics
"""

import argparse
from typing import Dict
from simulation_base.simulation_runner import parse_simulation_args, setup_simulation
from simulation_base.toxicity_analyzer import ToxicityAnalyzer
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.head_to_head_election import HeadToHeadElection
from simulation_base.actual_custom_election import ActualCustomElection
from simulation_base.election_process import ElectionProcess


def add_toxicity_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add toxicity-specific arguments to the parser."""
    parser.add_argument(
        "--toxic-bonus",
        type=float,
        default=0.25,
        help="Bonus with own party when using toxic tactics (default: 0.25)"
    )
    parser.add_argument(
        "--toxic-penalty",
        type=float,
        default=-1.0,
        help="Penalty with opposition party when using toxic tactics (default: -1.0)"
    )
    parser.add_argument(
        "--verbose-toxicity",
        action="store_true",
        help="Show detailed toxicity results for each district"
    )
    parser.add_argument(
        "--max-districts",
        type=int,
        default=None,
        help="Maximum number of districts to analyze (for testing)"
    )
    return parser


def get_election_process(state: str, primary_skew: float, election_type: str) -> ElectionProcess:
    """Get the appropriate election process for the given type."""
    if election_type == "primary":
        return ElectionWithPrimary(primary_skew=0, debug=False)
    elif election_type == "condorcet":
        return HeadToHeadElection(debug=False)
    elif election_type == "custom":
        return ActualCustomElection(state_abbr=state, primary_skew=primary_skew, debug=False)
    elif election_type == "irv":
        return InstantRunoffElection(debug=False)
    else:
        raise ValueError(f"Unknown election type: {election_type}")


def run_toxicity_tests(config, gaussian_generator, data_file: str, election_type: str, 
                      toxic_bonus: float, toxic_penalty: float, verbose: bool = False, 
                      max_districts: int = None):
    """Run toxicity tests using the comprehensive analyze_district_toxicity method."""
    print("=== Running Toxicity Tests ===")
    
    # Initialize toxicity analyzer
    analyzer = ToxicityAnalyzer(toxic_bonus, toxic_penalty)
    
    # Load district data directly
    from congressional_simulation import CongressionalSimulation
    simulation = CongressionalSimulation(config=config, gaussian_generator=gaussian_generator, election_type=election_type)
    districts = simulation.load_districts(data_file)
    
    # Limit districts if specified
    if max_districts:
        districts = districts[:max_districts]
        print(f"Analyzing first {max_districts} districts for testing...")
    
    print(f"Analyzing {len(districts)} districts...")
    
    # Run toxicity tests for each district
    print("\nRunning toxicity tests...")
    
    # Track statistics for non-toxic base elections
    non_toxic_stats = {
        'total_districts': 0,
        'toxic_success': 0,
        'toxic_twin_wins': 0,
        'opposition_wins': 0,
        'opponent_toxic_wins': 0,
        'third_candidate_wins': 0,
        'original_winner_wins': 0
    }
    
    # Track statistics for toxic base elections
    toxic_stats = {
        'total_districts': 0,
        'non_toxic_success': 0,
        'non_toxic_twin_wins': 0,
        'opposition_wins': 0,
        'third_candidate_wins': 0,
        'original_winner_wins': 0
    }
    
    for i, district in enumerate(districts):
        if verbose and i % 50 == 0:
            print(f"  Processing district {i+1}/{len(districts)}")
        
        # Generate the election definition for this district
        election_def = config.generate_definition(district, gaussian_generator)
        
        state_abbr = district.state
        election_process = get_election_process(state_abbr, config.primary_skew, election_type)
        # Use the comprehensive analysis method
        analysis = analyzer.analyze_district_toxicity(election_def, election_process, gaussian_generator)
        
        # Process non-toxic base scenario results
        non_toxic_stats['total_districts'] += 1
        twin_scenario = analysis['twin_scenario']['scenario']
        
        # Check if ANY candidate could win by adopting toxic tactics
        toxic_success = False
        
        # Check if toxic twin could win
        if twin_scenario == 'toxic_success':
            non_toxic_stats['toxic_twin_wins'] += 1
            toxic_success = True
        # Check if toxic opposition could win
        elif twin_scenario == 'toxic_success_flip':
            non_toxic_stats['opposition_wins'] += 1
            toxic_success = True
        # Check if individual opponents could win with toxic tactics
        elif analysis.get('toxic_success', False):
            non_toxic_stats['opponent_toxic_wins'] += 1
            toxic_success = True
        elif twin_scenario == 'toxic_failure_flip':
            non_toxic_stats['third_candidate_wins'] += 1
        elif twin_scenario == 'toxic_failure':
            non_toxic_stats['original_winner_wins'] += 1
        
        if toxic_success:
            non_toxic_stats['toxic_success'] += 1
        
        # Process toxic base scenario results
        toxic_stats['total_districts'] += 1
        toxic_base_analysis = analysis['toxic_base_analysis']
        
        # Non-toxic success: either non-toxic twin wins OR opposition wins (rejecting toxic tactics works)
        if toxic_base_analysis['non_toxic_twin_wins'] or toxic_base_analysis['opposition_wins']:
            toxic_stats['non_toxic_success'] += 1
            if toxic_base_analysis['non_toxic_twin_wins']:
                toxic_stats['non_toxic_twin_wins'] += 1
            elif toxic_base_analysis['opposition_wins']:
                toxic_stats['opposition_wins'] += 1
        else:
            toxic_stats['original_winner_wins'] += 1
            
    
    return {
        'non_toxic_stats': non_toxic_stats,
        'toxic_stats': toxic_stats
    }


def print_toxicity_results(analysis: Dict, toxic_bonus: float, toxic_penalty: float):
    """Print the toxicity test results."""
    print("\n" + "="*60)
    print("TOXICITY TEST RESULTS")
    print("="*60)
    
    print("\nToxicity Parameters:")
    print(f"  Toxic Bonus (own party): +{toxic_bonus}")
    print(f"  Toxic Penalty (opposition): {toxic_penalty}")
    
    non_toxic_stats = analysis['non_toxic_stats']
    toxic_stats = analysis['toxic_stats']
    
    print("\n=== NON-TOXIC BASE ELECTIONS ===")
    print(f"Districts analyzed: {non_toxic_stats['total_districts']}")
    
    if non_toxic_stats['total_districts'] > 0:
        toxic_success_pct = (non_toxic_stats['toxic_success'] / non_toxic_stats['total_districts']) * 100
        toxic_twin_pct = (non_toxic_stats['toxic_twin_wins'] / non_toxic_stats['total_districts']) * 100
        opposition_pct = (non_toxic_stats['opposition_wins'] / non_toxic_stats['total_districts']) * 100
        third_candidate_pct = (non_toxic_stats['third_candidate_wins'] / non_toxic_stats['total_districts']) * 100
        original_winner_pct = (non_toxic_stats['original_winner_wins'] / non_toxic_stats['total_districts']) * 100
        
        opponent_toxic_pct = (non_toxic_stats['opponent_toxic_wins'] / non_toxic_stats['total_districts']) * 100
        
        print(f"  Toxic success: {non_toxic_stats['toxic_success']} ({toxic_success_pct:.1f}%)")
        print(f"    - Toxic twin wins: {non_toxic_stats['toxic_twin_wins']} ({toxic_twin_pct:.1f}%)")
        print(f"    - Opposition wins: {non_toxic_stats['opposition_wins']} ({opposition_pct:.1f}%)")
        print(f"    - Opponent toxic wins: {non_toxic_stats['opponent_toxic_wins']} ({opponent_toxic_pct:.1f}%)")
        print(f"  Third candidate wins: {non_toxic_stats['third_candidate_wins']} ({third_candidate_pct:.1f}%)")
        print(f"  Original winner wins: {non_toxic_stats['original_winner_wins']} ({original_winner_pct:.1f}%)")
    
    print("\n=== TOXIC BASE ELECTIONS ===")
    print(f"Districts analyzed: {toxic_stats['total_districts']}")
    
    if toxic_stats['total_districts'] > 0:
        non_toxic_success_pct = (toxic_stats['non_toxic_success'] / toxic_stats['total_districts']) * 100
        non_toxic_twin_pct = (toxic_stats['non_toxic_twin_wins'] / toxic_stats['total_districts']) * 100
        opposition_pct = (toxic_stats['opposition_wins'] / toxic_stats['total_districts']) * 100
        original_winner_pct = (toxic_stats['original_winner_wins'] / toxic_stats['total_districts']) * 100
        
        print(f"  Non-toxic success: {toxic_stats['non_toxic_success']} ({non_toxic_success_pct:.1f}%)")
        print(f"    - Non-toxic twin wins: {toxic_stats['non_toxic_twin_wins']} ({non_toxic_twin_pct:.1f}%)")
        print(f"    - Opposition wins: {toxic_stats['opposition_wins']} ({opposition_pct:.1f}%)")
        print(f"  Original winner wins: {toxic_stats['original_winner_wins']} ({original_winner_pct:.1f}%)")
    
    print("\n=== SUMMARY ===")
    total_districts = non_toxic_stats['total_districts']
    if total_districts > 0:
        print(f"  Percentage of toxic success: {(non_toxic_stats['toxic_success'] / total_districts) * 100:.1f}%")
        print(f"  Percentage of non-toxic success: {(toxic_stats['non_toxic_success'] / total_districts) * 100:.1f}%")
        print(f"  Percentage of toxic twin success: {(non_toxic_stats['toxic_twin_wins'] / total_districts) * 100:.1f}%")


def main():
    """Main function for toxicity tests."""
    # Parse arguments
    parser = parse_simulation_args("Test the effects of toxic political tactics on election outcomes")
    parser = add_toxicity_args(parser)
    args = parser.parse_args()
    
    print("Toxicity Tests for Election Simulations")
    print("="*50)
    
    # Setup simulation
    config, gaussian_generator = setup_simulation(args)
    
    # Run toxicity tests directly (no redundant base simulation)
    analysis = run_toxicity_tests(
        config, gaussian_generator, args.data_file, args.election_type, 
        args.toxic_bonus, args.toxic_penalty, 
        args.verbose_toxicity, args.max_districts
    )
    
    # Print results
    print_toxicity_results(analysis, args.toxic_bonus, args.toxic_penalty)
    
    # Save results if output specified
    if args.output and args.output != "simulation_results.json":
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
