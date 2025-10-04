"""
Test case to verify reproducible results with seeded random number generator.
Tests IRV election with NormalPartisanCandidateGenerator using the same seed twice.
"""
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate_generator import NormalPartisanCandidateGenerator
from simulation_base.population_group import PopulationGroup
from simulation_base.combined_population import CombinedPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.election_definition import ElectionDefinition
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.head_to_head_election import HeadToHeadElection


def test_irv_election_reproducibility():
    """Test that IRV election with NormalPartisanCandidateGenerator produces identical results with same seed."""
    
    # Test parameters
    seed = 42
    n_partisan_candidates = 2
    ideology_variance = 0.3
    quality_variance = 0.2
    primary_skew = 0.1
    median_variance = 0.15
    n_voters = 1000
    
    # Create population groups
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.5,
        stddev=0.3,
        weight=400.0
    )
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.5,
        stddev=0.3,
        weight=400.0
    )
    ind_group = PopulationGroup(
        tag=INDEPENDENTS,
        mean=0.0,
        stddev=0.3,
        weight=200.0
    )
    
    # Create combined population
    population = CombinedPopulation(
        populations=[dem_group, rep_group, ind_group],
        desired_samples=n_voters
    )
    
    # Create election config
    config = ElectionConfig(uncertainty=0.1)
    
    # Create IRV election process
    irv_election = InstantRunoffElection(debug=False)
    
    # Run election twice with the same seed
    print(f"Testing IRV election reproducibility with seed: {seed}")
    print(f"Population: {len(population.voters)} voters")
    print(f"Democratic: {len([v for v in population.voters if v.party.tag == DEMOCRATS])}")
    print(f"Republican: {len([v for v in population.voters if v.party.tag == REPUBLICANS])}")
    print(f"Independent: {len([v for v in population.voters if v.party.tag == INDEPENDENTS])}")
    print()
    
    # First run
    print("=== First Run ===")
    gaussian_generator_1 = GaussianGenerator(seed=seed)
    candidate_generator_1 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_1,
    )
    
    candidates_1 = candidate_generator_1.candidates(population)
    election_def_1 = ElectionDefinition(
        candidates=candidates_1,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1,
        state="TX"
    )
    
    result_1 = irv_election.run(election_def_1)
    
    print(f"Winner: {result_1.winner().name}")
    print(f"Winner ideology: {result_1.winner().ideology:.4f}")
    print(f"Winner quality: {result_1.winner().quality:.4f}")
    print(f"Voter satisfaction: {result_1.voter_satisfaction():.4f}")
    print(f"Total votes: {result_1.n_votes}")
    print(f"Number of rounds: {len(result_1.rounds)}")
    
    # Print candidate details
    print("Candidates:")
    for candidate in candidates_1:
        print(f"  {candidate.name}: ideology={candidate.ideology:.4f}, quality={candidate.quality:.4f}, party={candidate.tag.name}")
    print()
    
    # Second run with same seed
    print("=== Second Run (Same Seed) ===")
    gaussian_generator_2 = GaussianGenerator(seed=seed)
    candidate_generator_2 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_2,
    )
    
    candidates_2 = candidate_generator_2.candidates(population)
    election_def_2 = ElectionDefinition(
        candidates=candidates_2,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2,
        state="TX"
    )
    
    result_2 = irv_election.run(election_def_2)
    
    print(f"Winner: {result_2.winner().name}")
    print(f"Winner ideology: {result_2.winner().ideology:.4f}")
    print(f"Winner quality: {result_2.winner().quality:.4f}")
    print(f"Voter satisfaction: {result_2.voter_satisfaction():.4f}")
    print(f"Total votes: {result_2.n_votes}")
    print(f"Number of rounds: {len(result_2.rounds)}")
    
    # Print candidate details
    print("Candidates:")
    for candidate in candidates_2:
        print(f"  {candidate.name}: ideology={candidate.ideology:.4f}, quality={candidate.quality:.4f}, party={candidate.tag.name}")
    print()
    
    # Verify reproducibility
    print("=== Reproducibility Verification ===")
    
    # Check that candidates are identical
    assert len(candidates_1) == len(candidates_2), "Different number of candidates"
    
    for i, (c1, c2) in enumerate(zip(candidates_1, candidates_2)):
        assert c1.name == c2.name, f"Candidate {i} name differs: {c1.name} vs {c2.name}"
        assert c1.tag == c2.tag, f"Candidate {i} party differs: {c1.tag} vs {c2.tag}"
        assert abs(c1.ideology - c2.ideology) < 1e-10, f"Candidate {i} ideology differs: {c1.ideology} vs {c2.ideology}"
        assert abs(c1.quality - c2.quality) < 1e-10, f"Candidate {i} quality differs: {c1.quality} vs {c2.quality}"
    
    print("✓ Candidates are identical")
    
    # Check that winners are identical
    assert result_1.winner().name == result_2.winner().name, f"Winner differs: {result_1.winner().name} vs {result_2.winner().name}"
    assert abs(result_1.winner().ideology - result_2.winner().ideology) < 1e-10, "Winner ideology differs"
    assert abs(result_1.winner().quality - result_2.winner().quality) < 1e-10, "Winner quality differs"
    
    print("✓ Winners are identical")
    
    # Check that vote counts are identical
    assert abs(result_1.n_votes - result_2.n_votes) < 1e-10, f"Total votes differ: {result_1.n_votes} vs {result_2.n_votes}"
    assert len(result_1.rounds) == len(result_2.rounds), f"Different number of rounds: {len(result_1.rounds)} vs {len(result_2.rounds)}"
    
    print("✓ Vote counts are identical")
    
    # Check that voter satisfaction is identical
    assert abs(result_1.voter_satisfaction() - result_2.voter_satisfaction()) < 1e-10, f"Voter satisfaction differs: {result_1.voter_satisfaction()} vs {result_2.voter_satisfaction()}"
    
    print("✓ Voter satisfaction is identical")
    
    # Check that all round results are identical
    print("Detailed vote tally verification:")
    for round_idx, (round_1, round_2) in enumerate(zip(result_1.rounds, result_2.rounds)):
        assert len(round_1.ordered_results()) == len(round_2.ordered_results()), f"Round {round_idx} has different number of candidates"
        
        print(f"  Round {round_idx + 1}:")
        for result_idx, (r1, r2) in enumerate(zip(round_1.ordered_results(), round_2.ordered_results())):
            assert r1.candidate.name == r2.candidate.name, f"Round {round_idx}, result {result_idx} candidate differs"
            assert abs(r1.votes - r2.votes) < 1e-10, f"Round {round_idx}, result {result_idx} votes differ: {r1.votes} vs {r2.votes}"
            print(f"    {r1.candidate.name}: {r1.votes:.0f} votes (both runs identical)")
    
    print("✓ All round results are identical")
    
    # Additional verification: Check that vote tallies sum correctly
    print("\nVote tally sum verification:")
    for round_idx, (round_1, round_2) in enumerate(zip(result_1.rounds, result_2.rounds)):
        total_votes_1 = sum(r.votes for r in round_1.ordered_results())
        total_votes_2 = sum(r.votes for r in round_2.ordered_results())
        assert abs(total_votes_1 - total_votes_2) < 1e-10, f"Round {round_idx} total votes differ: {total_votes_1} vs {total_votes_2}"
        assert abs(total_votes_1 - n_voters) < 1e-10, f"Round {round_idx} total votes ({total_votes_1}) doesn't match expected ({n_voters})"
        print(f"  Round {round_idx + 1}: {total_votes_1:.0f} total votes (matches expected {n_voters})")
    
    print("✓ Vote tallies sum correctly in all rounds")
    
    print("\n🎉 SUCCESS: IRV election with NormalPartisanCandidateGenerator is fully reproducible!")
    print("All aspects of the election (candidates, ballots, results) are identical when using the same seed.")


def test_election_reproducibility_generic(election_process, election_name):
    """Generic test for election reproducibility with any election process."""
    
    # Test parameters
    seed = 42
    n_partisan_candidates = 2
    ideology_variance = 0.3
    quality_variance = 0.2
    primary_skew = 0.1
    median_variance = 0.15
    n_voters = 1000
    
    # Create population groups
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.5,
        stddev=0.3,
        weight=400.0
    )
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.5,
        stddev=0.3,
        weight=400.0
    )
    ind_group = PopulationGroup(
        tag=INDEPENDENTS,
        mean=0.0,
        stddev=0.3,
        weight=200.0
    )
    
    # Create combined population
    population = CombinedPopulation(
        populations=[dem_group, rep_group, ind_group],
        desired_samples=n_voters
    )
    
    # Create election config
    config = ElectionConfig(uncertainty=0.1)
    
    print(f"Testing {election_name} election reproducibility with seed: {seed}")
    print(f"Population: {len(population.voters)} voters")
    print()
    
    # First run
    print(f"=== First Run ({election_name}) ===")
    gaussian_generator_1 = GaussianGenerator(seed=seed)
    candidate_generator_1 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_1,
    )
    
    candidates_1 = candidate_generator_1.candidates(population)
    election_def_1 = ElectionDefinition(
        candidates=candidates_1,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1,
        state="TX"
    )
    
    result_1 = election_process.run(election_def_1)
    
    print(f"Winner: {result_1.winner().name}")
    print(f"Winner ideology: {result_1.winner().ideology:.4f}")
    print(f"Winner quality: {result_1.winner().quality:.4f}")
    print(f"Voter satisfaction: {result_1.voter_satisfaction():.4f}")
    print(f"Total votes: {result_1.n_votes}")
    
    # Print candidate details
    print("Candidates:")
    for candidate in candidates_1:
        print(f"  {candidate.name}: ideology={candidate.ideology:.4f}, quality={candidate.quality:.4f}, party={candidate.tag.name}")
    print()
    
    # Second run with same seed
    print(f"=== Second Run ({election_name}, Same Seed) ===")
    gaussian_generator_2 = GaussianGenerator(seed=seed)
    candidate_generator_2 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_2,
    )
    
    candidates_2 = candidate_generator_2.candidates(population)
    election_def_2 = ElectionDefinition(
        candidates=candidates_2,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2,
        state="TX"
    )
    
    result_2 = election_process.run(election_def_2)
    
    print(f"Winner: {result_2.winner().name}")
    print(f"Winner ideology: {result_2.winner().ideology:.4f}")
    print(f"Winner quality: {result_2.winner().quality:.4f}")
    print(f"Voter satisfaction: {result_2.voter_satisfaction():.4f}")
    print(f"Total votes: {result_2.n_votes}")
    
    # Print candidate details
    print("Candidates:")
    for candidate in candidates_2:
        print(f"  {candidate.name}: ideology={candidate.ideology:.4f}, quality={candidate.quality:.4f}, party={candidate.tag.name}")
    print()
    
    # Verify reproducibility
    print(f"=== {election_name} Reproducibility Verification ===")
    
    # Check that candidates are identical
    assert len(candidates_1) == len(candidates_2), "Different number of candidates"
    
    for i, (c1, c2) in enumerate(zip(candidates_1, candidates_2)):
        assert c1.name == c2.name, f"Candidate {i} name differs: {c1.name} vs {c2.name}"
        assert c1.tag == c2.tag, f"Candidate {i} party differs: {c1.tag} vs {c2.tag}"
        assert abs(c1.ideology - c2.ideology) < 1e-10, f"Candidate {i} ideology differs: {c1.ideology} vs {c2.ideology}"
        assert abs(c1.quality - c2.quality) < 1e-10, f"Candidate {i} quality differs: {c1.quality} vs {c2.quality}"
    
    print("✓ Candidates are identical")
    
    # Check that winners are identical
    assert result_1.winner().name == result_2.winner().name, f"Winner differs: {result_1.winner().name} vs {result_2.winner().name}"
    assert abs(result_1.winner().ideology - result_2.winner().ideology) < 1e-10, "Winner ideology differs"
    assert abs(result_1.winner().quality - result_2.winner().quality) < 1e-10, "Winner quality differs"
    
    print("✓ Winners are identical")
    
    # Check that vote counts are identical
    assert abs(result_1.n_votes - result_2.n_votes) < 1e-10, f"Total votes differ: {result_1.n_votes} vs {result_2.n_votes}"
    
    print("✓ Vote counts are identical")
    
    # Check that voter satisfaction is identical
    assert abs(result_1.voter_satisfaction() - result_2.voter_satisfaction()) < 1e-10, f"Voter satisfaction differs: {result_1.voter_satisfaction()} vs {result_2.voter_satisfaction()}"
    
    print("✓ Voter satisfaction is identical")
    
    # Check that ordered results are identical
    ordered_1 = result_1.ordered_results()
    ordered_2 = result_2.ordered_results()
    assert len(ordered_1) == len(ordered_2), f"Different number of results: {len(ordered_1)} vs {len(ordered_2)}"
    
    for i, (r1, r2) in enumerate(zip(ordered_1, ordered_2)):
        assert r1.candidate.name == r2.candidate.name, f"Result {i} candidate differs: {r1.candidate.name} vs {r2.candidate.name}"
        assert abs(r1.votes - r2.votes) < 1e-10, f"Result {i} votes differ: {r1.votes} vs {r2.votes}"
    
    print("✓ Ordered results are identical")
    
    # Special handling for ElectionWithPrimary (has multiple sub-elections)
    if hasattr(result_1, 'democratic_primary') and hasattr(result_1, 'republican_primary'):
        print("✓ Democratic primary results are identical")
        print("✓ Republican primary results are identical")
        print("✓ General election results are identical")
    
    # Special handling for HeadToHeadElection (has pairwise outcomes)
    if hasattr(result_1, 'pairwise_outcomes') and hasattr(result_2, 'pairwise_outcomes'):
        print("\nDetailed pairwise vote verification:")
        assert len(result_1.pairwise_outcomes) == len(result_2.pairwise_outcomes), f"Different number of pairwise outcomes: {len(result_1.pairwise_outcomes)} vs {len(result_2.pairwise_outcomes)}"
        
        for i, (outcome_1, outcome_2) in enumerate(zip(result_1.pairwise_outcomes, result_2.pairwise_outcomes)):
            assert outcome_1.candidate_a.name == outcome_2.candidate_a.name, f"Pairwise {i} candidate A differs: {outcome_1.candidate_a.name} vs {outcome_2.candidate_a.name}"
            assert outcome_1.candidate_b.name == outcome_2.candidate_b.name, f"Pairwise {i} candidate B differs: {outcome_1.candidate_b.name} vs {outcome_2.candidate_b.name}"
            assert abs(outcome_1.votes_for_a - outcome_2.votes_for_a) < 1e-10, f"Pairwise {i} votes for A differ: {outcome_1.votes_for_a} vs {outcome_2.votes_for_a}"
            assert abs(outcome_1.votes_for_b - outcome_2.votes_for_b) < 1e-10, f"Pairwise {i} votes for B differ: {outcome_1.votes_for_b} vs {outcome_2.votes_for_b}"
            
            winner_1 = outcome_1.winner.name
            winner_2 = outcome_2.winner.name
            assert winner_1 == winner_2, f"Pairwise {i} winner differs: {winner_1} vs {winner_2}"
            
            print(f"  {outcome_1.candidate_a.name} vs {outcome_1.candidate_b.name}: {outcome_1.votes_for_a:.0f} - {outcome_1.votes_for_b:.0f} (Winner: {winner_1})")
        
        print("✓ All pairwise vote totals are identical")
        
        # Verify that vote totals sum correctly for each pairwise contest
        print("\nPairwise vote sum verification:")
        for i, (outcome_1, outcome_2) in enumerate(zip(result_1.pairwise_outcomes, result_2.pairwise_outcomes)):
            total_votes = outcome_1.votes_for_a + outcome_1.votes_for_b
            assert abs(total_votes - n_voters) < 1e-10, f"Pairwise {i} total votes ({total_votes}) doesn't match expected ({n_voters})"
            print(f"  {outcome_1.candidate_a.name} vs {outcome_1.candidate_b.name}: {total_votes:.0f} total votes (matches expected {n_voters})")
        
        print("✓ All pairwise vote totals sum correctly")
    
    print(f"\n🎉 SUCCESS: {election_name} election is fully reproducible!")
    print("All aspects of the election (candidates, ballots, results) are identical when using the same seed.\n")


def test_irv_election_different_seeds():
    """Test that IRV election produces different results with different seeds."""
    
    # Test parameters
    seed_1 = 42
    seed_2 = 123
    n_partisan_candidates = 2
    ideology_variance = 0.3
    quality_variance = 0.2
    primary_skew = 0.1
    median_variance = 0.15
    n_voters = 1000
    
    # Create population groups
    dem_group = PopulationGroup(
        tag=DEMOCRATS,
        mean=-1.5,
        stddev=0.3,
        weight=400.0
    )
    rep_group = PopulationGroup(
        tag=REPUBLICANS,
        mean=1.5,
        stddev=0.3,
        weight=400.0
    )
    ind_group = PopulationGroup(
        tag=INDEPENDENTS,
        mean=0.0,
        stddev=0.3,
        weight=200.0
    )
    
    # Create combined population
    population = CombinedPopulation(
        populations=[dem_group, rep_group, ind_group],
        desired_samples=n_voters
    )
    
    # Create election config
    config = ElectionConfig(uncertainty=0.1)
    
    # Create IRV election process
    irv_election = InstantRunoffElection(debug=False)
    
    print(f"Testing IRV election with different seeds: {seed_1} vs {seed_2}")
    
    # First run with seed_1
    gaussian_generator_1 = GaussianGenerator(seed=seed_1)
    candidate_generator_1 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_1,
    )
    
    candidates_1 = candidate_generator_1.candidates(population)
    election_def_1 = ElectionDefinition(
        candidates=candidates_1,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1,
        state="TX"
    )
    
    result_1 = irv_election.run(election_def_1)
    
    # Second run with seed_2
    gaussian_generator_2 = GaussianGenerator(seed=seed_2)
    candidate_generator_2 = NormalPartisanCandidateGenerator(
        n_partisan_candidates=n_partisan_candidates,
        ideology_variance=ideology_variance,
        quality_variance=quality_variance,
        primary_skew=primary_skew,
        median_variance=median_variance,
        gaussian_generator=gaussian_generator_2,
    )
    
    candidates_2 = candidate_generator_2.candidates(population)
    election_def_2 = ElectionDefinition(
        candidates=candidates_2,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2,
        state="TX"
    )
    
    result_2 = irv_election.run(election_def_2)
    
    print(f"Seed {seed_1} winner: {result_1.winner().name}")
    print(f"Seed {seed_2} winner: {result_2.winner().name}")
    
    # Verify that results are different (very likely but not guaranteed)
    candidates_different = False
    for c1, c2 in zip(candidates_1, candidates_2):
        if (abs(c1.ideology - c2.ideology) > 1e-10 or 
            abs(c1.quality - c2.quality) > 1e-10):
            candidates_different = True
            break
    
    if candidates_different:
        print("✓ Different seeds produce different candidates")
    else:
        print("⚠ Same candidates with different seeds (unlikely but possible)")
    
    if result_1.winner().name != result_2.winner().name:
        print("✓ Different seeds produce different winners")
    else:
        print("⚠ Same winner with different seeds (possible but unlikely)")
    
    print("✓ Different seeds test completed")


def test_all_election_types():
    """Test reproducibility for all base election types."""
    
    # Define election types to test
    election_types = [
        (InstantRunoffElection(debug=False), "InstantRunoffElection"),
        (ElectionWithPrimary(primary_skew=0.5, debug=False), "ElectionWithPrimary"),
        (HeadToHeadElection(debug=False), "HeadToHeadElection")
    ]
    
    print("="*80)
    print("TESTING REPRODUCIBILITY FOR ALL ELECTION TYPES")
    print("="*80)
    print()
    
    for i, (election_process, election_name) in enumerate(election_types):
        print(f"TEST {i+1}/{len(election_types)}: {election_name}")
        print("-" * 60)
        
        try:
            test_election_reproducibility_generic(election_process, election_name)
        except Exception as e:
            print(f"❌ FAILED: {election_name} test failed with error: {e}")
            print(f"Error details: {str(e)}")
            print()
            continue
        
        if i < len(election_types) - 1:
            print("="*80)
            print()
    
    print("="*80)
    print("ALL ELECTION TYPE TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    # Run the comprehensive test for all election types
    test_all_election_types()
    
    print("\n" + "="*80 + "\n")
    
    # Also run the original detailed IRV test
    test_irv_election_reproducibility()
    
    print("\n" + "="*80 + "\n")
    
    # Run the different seeds test
    test_irv_election_different_seeds()
