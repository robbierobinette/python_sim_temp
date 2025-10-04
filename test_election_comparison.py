#!/usr/bin/env python3
"""
Test script comparing ComposableElection vs ElectionWithPrimary with identical seeded generators.
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

def test_election_comparison():
    """Test that ComposableElection produces the same results as ElectionWithPrimary."""
    print("Testing ComposableElection vs ElectionWithPrimary comparison...")
    
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
    print(f"Democratic voters: {len([v for v in population.voters if v.party.tag == DEMOCRATS])}")
    print(f"Republican voters: {len([v for v in population.voters if v.party.tag == REPUBLICANS])}")
    print(f"Independent voters: {len([v for v in population.voters if v.party.tag == INDEPENDENTS])}")
    print()
    
    # Test 1: ElectionWithPrimary (original implementation)
    print("=== Test 1: ElectionWithPrimary (Original) ===")
    election_def_1 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1
    )
    
    original_election = ElectionWithPrimary(primary_skew=0.5, debug=True)
    original_result = original_election.run(election_def_1)
    
    print(f"Original winner: {original_result.winner().name}")
    print(f"Original voter satisfaction: {original_result.voter_satisfaction():.3f}")
    print("Original general election results:")
    for result in original_result.general_election.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    print()
    
    # Test 2: ComposableElection with ClosedPrimary
    print("=== Test 2: ComposableElection with ClosedPrimary ===")
    election_def_2 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2
    )
    
    # Create closed primary with same settings as ElectionWithPrimary
    primary_config = ClosedPrimaryConfig(use_runoff=False, primary_skew=0.5)
    closed_primary = ClosedPrimary(config=primary_config, debug=True)
    general_process = InstantRunoffElection(debug=True)
    composable_election = ComposableElection(closed_primary, general_process, debug=True)
    
    composable_result = composable_election.run(election_def_2)
    
    print(f"Composable winner: {composable_result.winner().name}")
    print(f"Composable voter satisfaction: {composable_result.voter_satisfaction():.3f}")
    print("Composable general election results:")
    for result in composable_result.general_result.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    print()
    
    # Compare results
    print("=== COMPARISON RESULTS ===")
    print(f"Winners match: {original_result.winner().name == composable_result.winner().name}")
    print(f"Voter satisfaction difference: {abs(original_result.voter_satisfaction() - composable_result.voter_satisfaction()):.6f}")
    
    # Compare general election results
    original_general = original_result.general_election.ordered_results()
    composable_general = composable_result.general_result.ordered_results()
    
    print(f"General election candidate count match: {len(original_general) == len(composable_general)}")
    
    if len(original_general) == len(composable_general):
        vote_differences = []
        for i, (orig, comp) in enumerate(zip(original_general, composable_general)):
            vote_diff = abs(orig.votes - comp.votes)
            vote_differences.append(vote_diff)
            print(f"  {orig.candidate.name}: Original={orig.votes}, Composable={comp.votes}, Diff={vote_diff:.2f}")
        
        max_vote_diff = max(vote_differences) if vote_differences else 0
        print(f"Maximum vote difference: {max_vote_diff:.2f}")
        print(f"Results are identical: {max_vote_diff < 0.01}")
    else:
        print("ERROR: Different number of candidates in general election results")
    
    # Compare primary results
    print("\n=== PRIMARY COMPARISON ===")
    print("Original Democratic primary:")
    for result in original_result.democratic_primary.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print("Composable Democratic primary:")
    for result in composable_result.primary_result.democratic_primary.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print("Original Republican primary:")
    for result in original_result.republican_primary.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print("Composable Republican primary:")
    for result in composable_result.primary_result.republican_primary.ordered_results():
        print(f"  {result.candidate.name}: {result.votes}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_election_comparison()
