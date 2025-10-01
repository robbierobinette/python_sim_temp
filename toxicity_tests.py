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
from simulation_base.election_process import ElectionProcess
from simulation_base.election_definition import ElectionDefinition


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


def get_election_process(election_type: str) -> ElectionProcess:
    """Get the appropriate election process for the given type."""
    if election_type == "primary":
        return ElectionWithPrimary(primary_skew=0.25, debug=False)
    elif election_type == "condorcet":
        return HeadToHeadElection(debug=False)
    elif election_type == "irv":
        return InstantRunoffElection(debug=False)
    else:
        raise ValueError(f"Unknown election type: {election_type}")


def run_toxicity_tests(config, gaussian_generator, data_file: str, election_type: str, 
                      toxic_bonus: float, toxic_penalty: float, verbose: bool = False, 
                      max_districts: int = None):
    """Run toxicity tests using twin scenarios approach."""
    print("=== Running Toxicity Tests ===")
    
    # Initialize toxicity analyzer
    analyzer = ToxicityAnalyzer(toxic_bonus, toxic_penalty)
    
    # Get election process
    election_process = get_election_process(election_type)
    
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
        'toxic_twin_wins': 0,
        'opposition_wins': 0,
        'third_candidate_wins': 0,
        'original_winner_wins': 0
    }
    
    # Track statistics for toxic base elections
    toxic_stats = {
        'total_districts': 0,
        'non_toxic_twin_wins': 0,
        'opposition_wins': 0,
        'third_candidate_wins': 0,
        'original_winner_wins': 0
    }
    
    for i, district in enumerate(districts):
        if verbose and i % 50 == 0:
            print(f"  Processing district {i+1}/{len(districts)}")
        
        try:
            # Generate the election definition for this district
            election_def = config.generate_definition(district, gaussian_generator)
            
            # Test non-toxic base scenario
            non_toxic_result = analyzer.test_twin_scenarios(election_def, election_process, gaussian_generator)
            non_toxic_stats['total_districts'] += 1
            
            if non_toxic_result['scenario'] == 'toxic_success':
                non_toxic_stats['toxic_twin_wins'] += 1
            elif non_toxic_result['scenario'] == 'toxic_success_flip':
                non_toxic_stats['opposition_wins'] += 1
            elif non_toxic_result['scenario'] == 'toxic_failure_flip':
                non_toxic_stats['third_candidate_wins'] += 1
            elif non_toxic_result['scenario'] == 'toxic_failure':
                non_toxic_stats['original_winner_wins'] += 1
            
            # Test toxic base scenario (create all-toxic election)
            toxic_candidates = [analyzer.apply_toxic_tactics(c) for c in election_def.candidates]
            toxic_election_def = ElectionDefinition(
                candidates=toxic_candidates,
                population=election_def.population,
                config=election_def.config,
                gaussian_generator=election_def.gaussian_generator
            )
            
            # Run toxic base election
            toxic_result = analyzer._run_election(toxic_election_def, election_process, gaussian_generator)
            toxic_winner = toxic_result.winner()
            
            # Find the original candidate by matching the toxic winner's ideology and tag
            original_candidate = None
            for candidate in election_def.candidates:
                if (candidate.ideology == toxic_winner.ideology and 
                    candidate.tag == toxic_winner.tag and
                    candidate.quality == toxic_winner.quality):
                    original_candidate = candidate
                    break
            
            # Always process toxic base scenario
            if original_candidate:
                # Create non-toxic twin (copy of original candidate)
                import copy
                non_toxic_twin = copy.deepcopy(original_candidate)
                non_toxic_twin.name = f"non-toxic-{original_candidate.name}"
                
                # Create election with non-toxic twin vs other toxic candidates
                non_toxic_candidates = []
                for i, candidate in enumerate(toxic_candidates):
                    if (candidate.ideology == toxic_winner.ideology and 
                        candidate.tag == toxic_winner.tag and
                        candidate.quality == toxic_winner.quality):
                        non_toxic_candidates.append(non_toxic_twin)
                    else:
                        non_toxic_candidates.append(candidate)
                
                non_toxic_election_def = ElectionDefinition(
                    candidates=non_toxic_candidates,
                    population=election_def.population,
                    config=election_def.config,
                    gaussian_generator=election_def.gaussian_generator
                )
                
                non_toxic_base_result = analyzer._run_election(non_toxic_election_def, election_process, gaussian_generator)
                non_toxic_base_winner = non_toxic_base_result.winner()
                
                toxic_stats['total_districts'] += 1
                
                if non_toxic_base_winner.name == non_toxic_twin.name:
                    toxic_stats['non_toxic_twin_wins'] += 1
                elif non_toxic_base_winner.tag != toxic_winner.tag:
                    toxic_stats['opposition_wins'] += 1
                else:
                    toxic_stats['original_winner_wins'] += 1
            
        except Exception as e:
            if verbose:
                print(f"  Error processing district {district.district}: {e}")
            continue
    
    return {
        'non_toxic_stats': non_toxic_stats,
        'toxic_stats': toxic_stats
    }


def print_toxicity_results(analysis: Dict, toxic_bonus: float, toxic_penalty: float):
    """Print the toxicity test results."""
    print("\n" + "="*60)
    print("TOXICITY TEST RESULTS")
    print("="*60)
    
    print(f"\nToxicity Parameters:")
    print(f"  Toxic Bonus (own party): +{toxic_bonus}")
    print(f"  Toxic Penalty (opposition): {toxic_penalty}")
    
    non_toxic_stats = analysis['non_toxic_stats']
    toxic_stats = analysis['toxic_stats']
    
    print(f"\n=== NON-TOXIC BASE ELECTIONS ===")
    print(f"Districts analyzed: {non_toxic_stats['total_districts']}")
    
    if non_toxic_stats['total_districts'] > 0:
        toxic_twin_pct = (non_toxic_stats['toxic_twin_wins'] / non_toxic_stats['total_districts']) * 100
        opposition_pct = (non_toxic_stats['opposition_wins'] / non_toxic_stats['total_districts']) * 100
        third_candidate_pct = (non_toxic_stats['third_candidate_wins'] / non_toxic_stats['total_districts']) * 100
        original_winner_pct = (non_toxic_stats['original_winner_wins'] / non_toxic_stats['total_districts']) * 100
        
        print(f"  Toxic twin could win: {non_toxic_stats['toxic_twin_wins']} ({toxic_twin_pct:.1f}%)")
        print(f"  Opposition candidate wins: {non_toxic_stats['opposition_wins']} ({opposition_pct:.1f}%)")
        print(f"  Third candidate wins: {non_toxic_stats['third_candidate_wins']} ({third_candidate_pct:.1f}%)")
        print(f"  Original winner wins: {non_toxic_stats['original_winner_wins']} ({original_winner_pct:.1f}%)")
    
    print(f"\n=== TOXIC BASE ELECTIONS ===")
    print(f"Districts analyzed: {toxic_stats['total_districts']}")
    
    if toxic_stats['total_districts'] > 0:
        non_toxic_twin_pct = (toxic_stats['non_toxic_twin_wins'] / toxic_stats['total_districts']) * 100
        opposition_pct = (toxic_stats['opposition_wins'] / toxic_stats['total_districts']) * 100
        original_winner_pct = (toxic_stats['original_winner_wins'] / toxic_stats['total_districts']) * 100
        
        print(f"  Non-toxic twin could win: {toxic_stats['non_toxic_twin_wins']} ({non_toxic_twin_pct:.1f}%)")
        print(f"  Opposition candidate wins: {toxic_stats['opposition_wins']} ({opposition_pct:.1f}%)")
        print(f"  Original winner wins: {toxic_stats['original_winner_wins']} ({original_winner_pct:.1f}%)")
    
    print(f"\n=== SUMMARY ===")
    total_districts = non_toxic_stats['total_districts']
    if total_districts > 0:
        toxic_effectiveness = ((non_toxic_stats['toxic_twin_wins'] + non_toxic_stats['opposition_wins'] + non_toxic_stats['third_candidate_wins']) / total_districts) * 100
        non_toxic_effectiveness = ((toxic_stats['non_toxic_twin_wins'] + toxic_stats['opposition_wins']) / total_districts) * 100
        
        print(f"  Toxic tactics effectiveness: {toxic_effectiveness:.1f}%")
        print(f"  Non-toxic tactics effectiveness: {non_toxic_effectiveness:.1f}%")


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
