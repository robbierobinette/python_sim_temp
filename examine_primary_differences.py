#!/usr/bin/env python3
"""
Examine how often different primary election types produce different winners.

This program compares different primary election types against a baseline
ElectionWithPrimary across various partisan leans to see how often they
produce different winners and how voter satisfaction differs.
"""

import json
import argparse
from typing import List, Any, Dict
from dataclasses import dataclass
from simulation_base.ballot import RCVBallot
from simulation_base.head_to_head_election import HeadToHeadElection
from simulation_base.simulation_runner import parse_simulation_args
from simulation_base.unit_population import UnitPopulation
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.election_definition import ElectionDefinition
from simulation_base.election_config import ElectionConfig

from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.candidate_generator import NormalPartisanCandidateGenerator


@dataclass
class ComparisonResult:
    """Result of comparing two election types."""
    partisan_lean: int
    iteration: int
    election_type: str
    winner_different: bool
    satisfaction_diff: float
    ideology_diff: float
    party_different: bool
    baseline_satisfaction: float
    alt_satisfaction: float


def load_election_types() -> List[Dict[str, Any]]:
    """Load unique election types from election_types.json."""
    with open("election_types.json", "r") as f:
        data = json.load(f)
    
    # Extract unique primary types
    primary_types = {}
    for state_data in data.values():
        key = name_from_election_config(state_data)
        if key not in primary_types:
            primary_types[key] = state_data
    
    return primary_types.values()


def create_election_process(election_type: Any, args: argparse.Namespace) -> Any:
    """Create an election process for the given type."""
    if election_type == "baseline":
        return ElectionWithPrimary(primary_skew=args.primary_skew, debug=False)
    else:
        # Create a composable election with the specific configuration
        return create_composable_election(election_type, args)


def create_composable_election(election_spec: Dict[str, Any], args: argparse.Namespace) -> Any:
    """Create a composable election from a configuration dictionary."""
    from simulation_base.composable_election import ComposableElection
    from simulation_base.closed_primary import ClosedPrimary
    from simulation_base.open_primary import OpenPrimary
    from simulation_base.topn_primary import TopNPrimary
    from simulation_base.simple_plurality import SimplePlurality
    from simulation_base.instant_runoff_election import InstantRunoffElection
    from simulation_base.plurality_with_runoff import PluralityWithRunoff
    
    debug = False

    # Create primary process
    primary_type = election_spec.get("primary")
    primary_runoff = election_spec.get("primary_runoff")

    
    if primary_type == "closed-partisan":
        primary_process = ClosedPrimary(use_runoff=primary_runoff, primary_skew=args.primary_skew, debug=debug)
    elif primary_type == "open-partisan":
        primary_process = OpenPrimary(use_runoff=primary_runoff, primary_skew=args.primary_skew, debug=debug)
    elif primary_type == "Louisiana-2":
        # special case for louisiana where there is no primary, but the general has a runoff.
        # Very similar to a california top-2 but using a general election electorate for the selection of the
        # top-2 and a shortcut for a candidate with > 50%.
        return PluralityWithRunoff(debug=debug)
    elif primary_type == "top-2":
        primary_process = TopNPrimary(n=2, primary_skew=args.primary_skew, debug=debug)
    elif primary_type == "top-4":
        primary_process = TopNPrimary(n=4, primary_skew=args.primary_skew, debug=debug)
    elif primary_type == "top-5":
        primary_process = TopNPrimary(n=5, primary_skew=args.primary_skew, debug=debug)
    elif primary_type == "semi-closed-partisan":
        # For now, treat semi-closed as closed
        primary_process = ClosedPrimary(use_runoff=primary_runoff, primary_skew=args.primary_skew, debug=debug)
    else:
        # Default to open-partisan
        primary_process = OpenPrimary(use_runoff=primary_runoff, primary_skew=args.primary_skew, debug=debug)
    
    # Create general process
    general_type = election_spec.get("general")
    general_runoff = election_spec.get("general_runoff", False)
    
    if general_type == "plurality":
        if general_runoff:
            general_process = PluralityWithRunoff(debug=debug)
        else:
            general_process = SimplePlurality(debug=debug)
    elif general_type == "instant runoff":
        general_process = InstantRunoffElection(debug=debug)
    elif general_type == "CCV":
        general_process = HeadToHeadElection(debug=debug)
    else:
        # Default to plurality
        if general_runoff:
            general_process = PluralityWithRunoff(debug=debug)
        else:
            general_process = SimplePlurality(debug=debug)
    
    return ComposableElection(primary_process, general_process, debug=debug)


def create_population(partisan_lean: int, seed: int, nvoters: int = 1000) -> Any:
    """Create a population with the given partisan lean and seed."""
    return UnitPopulation.create_from_lean(
        lean=partisan_lean,
        partisanship=1.0,
        stddev=1.0,
        skew_factor=0.0,
        n_voters=nvoters,
        seed=seed
    )


def create_candidates(population: Any, seed: int, args: Dict[str, Any]) -> List[Any]:
    """Create candidates for the population."""
    gaussian_generator = GaussianGenerator(seed)
    candidate_generator = NormalPartisanCandidateGenerator(
        n_partisan_candidates=args.candidates,
        ideology_variance=args.ideology_variance,
        quality_variance=args.quality_variance,
        primary_skew=args.primary_skew,
        median_variance=args.condorcet_variance,
        gaussian_generator=gaussian_generator,
    )
    return candidate_generator.candidates(population)



def compare_elections(baseline_result: Any, alt_result: Any, partisan_lean: int, 
                     iteration: int, election_type: str) -> ComparisonResult:
    """Compare two election results."""
    baseline_winner = baseline_result.winner()
    alt_winner = alt_result.winner()
    
    winner_different = baseline_winner.name != alt_winner.name
    party_different = baseline_winner.tag != alt_winner.tag

    if not winner_different:
        assert baseline_winner.ideology == alt_winner.ideology
    
    satisfaction_diff = alt_result.voter_satisfaction() - baseline_result.voter_satisfaction()

    ideology_diff = alt_winner.ideology - baseline_winner.ideology
    
    return ComparisonResult(
        partisan_lean=partisan_lean,
        iteration=iteration,
        election_type=election_type,
        winner_different=winner_different,
        satisfaction_diff=satisfaction_diff,
        ideology_diff=ideology_diff,
        party_different=party_different,
        baseline_satisfaction=baseline_result.voter_satisfaction(),
        alt_satisfaction=alt_result.voter_satisfaction()
    )

def create_ballots(voters: List[Any], candidates: List[Any], config: ElectionConfig, gaussian_generator: GaussianGenerator) -> List[RCVBallot]:
    return [RCVBallot(v, candidates, config, gaussian_generator) for v in voters]

def name_from_election_config(election_config: Dict[str, Any]) -> str:
    """Create a readable name for the election type."""
    primary_name = election_config['primary']
    if election_config.get('primary_runoff', False):
        primary_name += "-R"
    general_name = election_config['general']
    if election_config.get('general_runoff', False):
        general_name += "-R"
    return f"{primary_name}-{general_name}"

def run_comparison(partisan_lean: int, iteration: int, election_types: List[Dict[str, Any]], 
                  args: argparse.Namespace) -> List[ComparisonResult]:
    """Run comparison for a single partisan lean and iteration."""
    seed = args.seed + partisan_lean + iteration
    results = []
    
    # Create identical population and candidates for all election types
    gaussian_generator = GaussianGenerator(seed)
    population = create_population(partisan_lean, seed, args.nvoters)
    candidates = create_candidates(population, seed, args)
    config = ElectionConfig(uncertainty=args.uncertainty)
    ballots = create_ballots(population.voters, candidates, config, gaussian_generator)
    
    # Create election config
    
    # Run baseline election
    baseline_process = create_election_process("baseline", args)
    baseline_result = baseline_process.run(candidates, ballots)

    # names_to_test = set([ "top-2-plurality", ])
    
    # Run each alternative election type
    for election_config in election_types:
        alt_process = create_election_process(election_config, args)
        # Create a readable name for the election type
        election_type_name = name_from_election_config(election_config)
        # if election_type_name not in names_to_test:
            # continue
        
        alt_result = alt_process.run(candidates, ballots)
        # Compare results
        comparison = compare_elections(baseline_result, alt_result, partisan_lean, iteration, election_type_name)
        results.append(comparison)
    
    return results


def generate_summary(all_results: List[ComparisonResult]) -> None:
    """Generate and print summary statistics."""
    print("\n" + "="*80)
    print("PRIMARY ELECTION TYPE COMPARISON SUMMARY")
    print("="*80)
    
    # Group results by election type
    by_type = {}
    for result in all_results:
        if result.election_type not in by_type:
            by_type[result.election_type] = []
        by_type[result.election_type].append(result)
    
    # Print header
    print(f"{'Election Type':<40} {'Winner Diff %':<12} {'Avg Sat':<12} {'Avg Ideo Diff':<12} {'Party Diff %':<12}")
    print("-" * 120)
    
    # Print results for each type
    for election_type in sorted(by_type.keys()):
        results = by_type[election_type]
        
        winner_diff_pct = sum(1 for r in results if r.winner_different) / len(results) * 100
        avg_satisfaction = sum(r.alt_satisfaction for r in results) / len(results)
        avg_ideology_diff = sum(r.ideology_diff for r in results) / len(results)
        party_diff_pct = sum(1 for r in results if r.party_different) / len(results) * 100
        
        print(f"{election_type:<40} {winner_diff_pct:>10.1f}% {avg_satisfaction:>11.4f} {avg_ideology_diff:>11.4f} {party_diff_pct:>10.1f}%")
    
    print("\n" + "="*80)
    print("DETAILED RESULTS BY PARTISAN LEAN")
    print("="*80)
    
    # Group by partisan lean
    by_lean = {}
    for result in all_results:
        if result.partisan_lean not in by_lean:
            by_lean[result.partisan_lean] = {}
        if result.election_type not in by_lean[result.partisan_lean]:
            by_lean[result.partisan_lean][result.election_type] = []
        by_lean[result.partisan_lean][result.election_type].append(result)
    
    # Print detailed results
    for lean in sorted(by_lean.keys()):
        print(f"\nPartisan Lean: {lean}")
        print(f"{'Election Type':<40} {'Winner Diff %':<12} {'Avg Sat':<12} {'Avg Ideo Diff':<12}")
        print("-" * 60)
        
        for election_type in sorted(by_lean[lean].keys()):
            results = by_lean[lean][election_type]
            
            winner_diff_pct = sum(1 for r in results if r.winner_different) / len(results) * 100
            avg_satisfaction = sum(r.alt_satisfaction for r in results) / len(results)
            avg_ideology_diff = sum(r.ideology_diff for r in results) / len(results)
            
            print(f"{election_type:<40} {winner_diff_pct:>10.1f}% {avg_satisfaction:>11.4f} {avg_ideology_diff:>11.4f}")


def main():
    """Main entry point."""
    # Parse arguments
    parser = parse_simulation_args("Examine primary election type differences")
    args = parser.parse_args()
    
    # Load election types
    election_types = load_election_types()
    print(f"Found {len(election_types)} unique election types:")
    for i, config in enumerate(election_types):
        name = name_from_election_config(config)
        print(f"  {i+1}. {name}")
    
    # Note: baseline is handled separately
    
    # Run comparisons
    all_results = []
    partisan_leans = list(range(-20, 10, 10))  # -40 to 0 in steps of 5
    
    print(f"\nRunning comparisons for partisan leans: {partisan_leans}")
    print(f"Each lean will be tested {10} times with different seeds")
    print(f"Total comparisons: {len(partisan_leans)} leans × {10} iterations × {len(election_types)} types = {len(partisan_leans) * 10 * len(election_types)}")
    
    for lean in partisan_leans:
        print(f"\nProcessing partisan lean {lean}...")
        for iteration in range(100):
            if args.verbose:
                print(f"  Iteration {iteration + 1}/10")
            
            try:
                results = run_comparison(lean, iteration, election_types, args)
                all_results.extend(results)
            except Exception as e:
                print(f"ERROR: Failed at lean {lean}, iteration {iteration}: {e}")
                raise  # Re-raise as requested - any failure indicates coding problem
    
    # Generate summary
    generate_summary(all_results)
    
    print(f"\nCompleted {len(all_results)} comparisons successfully!")


if __name__ == "__main__":
    main()
