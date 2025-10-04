"""
Test case to verify HeadToHead election random tiebreaker functionality.
Creates a scenario with tied votes to test random winner selection.
"""
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate_generator import NormalPartisanCandidateGenerator
from simulation_base.population_group import PopulationGroup
from simulation_base.combined_population import CombinedPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.election_definition import ElectionDefinition
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.head_to_head_election import HeadToHeadElection
from simulation_base.candidate import Candidate


def create_tied_scenario():
    """Create a scenario where we can force ties in HeadToHead elections."""
    
    # Create a very simple population with only 2 voters to increase chance of ties
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.0,
        stddev=0.1,  # Very small stddev to make voters similar
        weight=1.0
    )
    
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.0,
        stddev=0.1,  # Very small stddev to make voters similar
        weight=1.0
    )
    
    population = CombinedPopulation(
        populations=[dem_group, rep_group],
        desired_samples=2  # Only 2 voters to maximize tie probability
    )
    
    # Create exactly 2 candidates with identical ideologies to force ties
    candidates = [
        Candidate("A", DEMOCRATS, -1.0, 0.0),  # Same ideology, same quality
        Candidate("B", REPUBLICANS, 1.0, 0.0),  # Same ideology, same quality
    ]
    
    return population, candidates


def test_head_to_head_tiebreaker():
    """Test that HeadToHead election randomly breaks ties."""
    
    print("Testing HeadToHead random tiebreaker functionality...")
    print("="*60)
    
    # Create tied scenario
    population, candidates = create_tied_scenario()
    
    # Create election config with high uncertainty to increase tie probability
    config = ElectionConfig(uncertainty=0.9)  # High uncertainty
    
    # Create HeadToHead election
    head_to_head = HeadToHeadElection(debug=False)
    
    print(f"Population: {len(population.voters)} voters")
    print(f"Candidates: {[c.name for c in candidates]}")
    print(f"Uncertainty: {config.uncertainty}")
    print()
    
    # Test with multiple seeds to see different tiebreaker outcomes
    seeds = [42, 123, 456, 789, 999]
    results = []
    
    for seed in seeds:
        print(f"--- Testing with seed {seed} ---")
        
        gaussian_generator = GaussianGenerator(seed=seed)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="TX"
        )
        
        result = head_to_head.run(election_def)
        
        print(f"Winner: {result.winner().name}")
        print(f"Voter satisfaction: {result.voter_satisfaction():.4f}")
        
        # Print pairwise outcomes
        print("Pairwise outcomes:")
        for outcome in result.pairwise_outcomes:
            tie_indicator = " [TIE]" if outcome.votes_for_a == outcome.votes_for_b else ""
            print(f"  {outcome.candidate_a.name} vs {outcome.candidate_b.name}: "
                  f"{outcome.votes_for_a:.0f} - {outcome.votes_for_b:.0f} "
                  f"(Winner: {outcome.winner.name}){tie_indicator}")
        
        results.append(result.winner().name)
        print()
    
    # Check if we got different winners (indicating tiebreaker is working)
    unique_winners = set(results)
    print(f"Winners across different seeds: {results}")
    print(f"Unique winners: {unique_winners}")
    
    if len(unique_winners) > 1:
        print("✓ SUCCESS: Random tiebreaker is working - different seeds produced different winners")
    else:
        print("⚠ WARNING: All seeds produced the same winner - tiebreaker may not be working or no ties occurred")
    
    print("\n" + "="*60)
    
    # Test reproducibility with same seed
    print("Testing reproducibility with same seed...")
    
    seed = 42
    gaussian_generator_1 = GaussianGenerator(seed=seed)
    gaussian_generator_2 = GaussianGenerator(seed=seed)
    
    election_def_1 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1,
        state="TX"
    )
    
    election_def_2 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2,
        state="TX"
    )
    
    result_1 = head_to_head.run(election_def_1)
    result_2 = head_to_head.run(election_def_2)
    
    print(f"Run 1 winner: {result_1.winner().name}")
    print(f"Run 2 winner: {result_2.winner().name}")
    
    if result_1.winner().name == result_2.winner().name:
        print("✓ SUCCESS: Same seed produces same winner (reproducible)")
    else:
        print("❌ FAILURE: Same seed produced different winners")
    
    # Verify pairwise outcomes are identical
    pairwise_identical = True
    for outcome_1, outcome_2 in zip(result_1.pairwise_outcomes, result_2.pairwise_outcomes):
        if (outcome_1.votes_for_a != outcome_2.votes_for_a or 
            outcome_1.votes_for_b != outcome_2.votes_for_b or
            outcome_1.winner.name != outcome_2.winner.name):
            pairwise_identical = False
            break
    
    if pairwise_identical:
        print("✓ SUCCESS: All pairwise outcomes are identical between runs")
    else:
        print("❌ FAILURE: Pairwise outcomes differ between runs")


if __name__ == "__main__":
    test_head_to_head_tiebreaker()
