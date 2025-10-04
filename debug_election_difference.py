#!/usr/bin/env python3
"""
Debug script to understand the difference between ElectionWithPrimary and ComposableElection.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_base.composable_election import ComposableElection
from simulation_base.closed_primary import ClosedPrimary, ClosedPrimaryConfig
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator

def debug_election_difference():
    """Debug the difference between the two election implementations."""
    # Create test candidates
    candidates = [
        Candidate("Dem-A", DEMOCRATS, -2.0, 0.8),
        Candidate("Dem-B", DEMOCRATS, -1.0, 0.7),
        Candidate("Dem-C", DEMOCRATS, -0.5, 0.6),
        Candidate("Rep-A", REPUBLICANS, 1.0, 0.7),
        Candidate("Rep-B", REPUBLICANS, 2.0, 0.8),
        Candidate("Ind-A", INDEPENDENTS, 0.0, 0.6),
    ]
    
    # Create test population
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.5,
        stddev=0.3,
        weight=150.0
    )
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.5,
        stddev=0.3,
        weight=150.0
    )
    ind_group = PopulationGroup(
        tag=INDEPENDENTS,
        mean=0.0,
        stddev=0.3,
        weight=50.0
    )
    
    population = CombinedPopulation(
        populations=[dem_group, rep_group, ind_group],
        desired_samples=350
    )
    
    # Create election config
    config = ElectionConfig(uncertainty=0.1)
    
    # Create seeded gaussian generators for identical results
    seed = 42
    gaussian_generator_1 = GaussianGenerator(seed=seed)
    gaussian_generator_2 = GaussianGenerator(seed=seed)
    
    print(f"Using seed: {seed}")
    print(f"Total voters: {len(population.voters)}")
    print()
    
    # Test 1: ElectionWithPrimary (original implementation)
    print("=== ElectionWithPrimary (Original) ===")
    election_def_1 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1,
        state="TX"

    )
    
    original_election = ElectionWithPrimary(primary_skew=0.5, debug=True)
    original_result = original_election.run(election_def_1)
    
    print(f"Original winner: {original_result.winner().name}")
    print()
    
    # Test 2: ComposableElection with ClosedPrimary
    print("=== ComposableElection with ClosedPrimary ===")
    election_def_2 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2,
        state="TX"
    )
    
    # Create closed primary with same settings as ElectionWithPrimary
    primary_config = ClosedPrimaryConfig(use_runoff=False, primary_skew=0.5)
    closed_primary = ClosedPrimary(config=primary_config, debug=True)
    general_process = InstantRunoffElection(debug=True)
    composable_election = ComposableElection(closed_primary, general_process, debug=True)
    
    composable_result = composable_election.run(election_def_2)
    
    print(f"Composable winner: {composable_result.winner().name}")
    print()
    
    # Compare final candidates
    print("=== FINAL CANDIDATES COMPARISON ===")
    print("Original final candidates:")
    for result in original_result.general_election.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print("Composable final candidates:")
    for result in composable_result.general_result.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print()
    print("=== CANDIDATE ORDERING COMPARISON ===")
    original_candidates = [r.candidate.name for r in original_result.general_election.ordered_results()]
    composable_candidates = [r.candidate.name for r in composable_result.general_result.ordered_results()]
    
    print(f"Original candidate order: {original_candidates}")
    print(f"Composable candidate order: {composable_candidates}")
    print(f"Orders match: {original_candidates == composable_candidates}")

if __name__ == "__main__":
    debug_election_difference()
