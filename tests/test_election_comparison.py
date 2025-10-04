"""
Test comparing ComposableElection vs ElectionWithPrimary with identical seeded generators.
"""
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


def test_composable_vs_original_election_with_primary():
    """Test that ComposableElection produces consistent results with ElectionWithPrimary."""
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
    # Use a fixed seed to ensure deterministic results
    seed = 12345
    gaussian_generator_1 = GaussianGenerator(seed=seed)
    gaussian_generator_2 = GaussianGenerator(seed=seed)
    
    # Test 1: ElectionWithPrimary (original implementation)
    election_def_1 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_1
    )
    
    original_election = ElectionWithPrimary(primary_skew=0.5, debug=False)
    original_result = original_election.run(election_def_1)
    
    # Test 2: ComposableElection with ClosedPrimary
    election_def_2 = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator_2
    )
    
    # Create closed primary with same settings as ElectionWithPrimary
    primary_config = ClosedPrimaryConfig(use_runoff=False, primary_skew=0.5)
    closed_primary = ClosedPrimary(config=primary_config, debug=False)
    general_process = InstantRunoffElection(debug=False)
    composable_election = ComposableElection(closed_primary, general_process, debug=False)
    
    composable_result = composable_election.run(election_def_2)
    
    # Compare results - focus on structural consistency rather than exact matches
    # Both implementations should produce valid election results with the same candidates
    
    # Verify both produce valid results
    assert original_result.winner() is not None, "Original election should have a winner"
    assert composable_result.winner() is not None, "Composable election should have a winner"
    
    # Verify both have the same final candidates (winners from primaries + independents)
    original_final_candidates = set(c.candidate.name for c in original_result.general_election.ordered_results())
    composable_final_candidates = set(c.candidate.name for c in composable_result.general_result.ordered_results())
    
    assert original_final_candidates == composable_final_candidates, f"Final candidates should match: {original_final_candidates} vs {composable_final_candidates}"
    
    # Verify both have the same primary winners
    original_dem_winner = original_result.democratic_primary.ordered_results()[0].candidate.name
    original_rep_winner = original_result.republican_primary.ordered_results()[0].candidate.name
    
    composable_dem_winner = composable_result.primary_result.democratic_primary.ordered_results()[0].candidate.name
    composable_rep_winner = composable_result.primary_result.republican_primary.ordered_results()[0].candidate.name
    
    assert original_dem_winner == composable_dem_winner, f"Democratic primary winners should match: {original_dem_winner} vs {composable_dem_winner}"
    assert original_rep_winner == composable_rep_winner, f"Republican primary winners should match: {original_rep_winner} vs {composable_rep_winner}"
    
    # Verify voter satisfaction is reasonable (not negative or > 1)
    assert 0 <= original_result.voter_satisfaction() <= 1, "Original voter satisfaction should be valid"
    assert 0 <= composable_result.voter_satisfaction() <= 1, "Composable voter satisfaction should be valid"


def test_composable_election_with_runoff():
    """Test ComposableElection with runoff enabled in ClosedPrimary."""
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
    gaussian_generator = GaussianGenerator(seed=123)
    
    election_def = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator
    )
    
    # Create closed primary with runoff enabled
    primary_config = ClosedPrimaryConfig(use_runoff=True, runoff_threshold=0.5, primary_skew=0.5)
    closed_primary = ClosedPrimary(config=primary_config, debug=False)
    general_process = InstantRunoffElection(debug=False)
    composable_election = ComposableElection(closed_primary, general_process, debug=False)
    
    result = composable_election.run(election_def)
    
    # Basic assertions
    assert result.winner() is not None, "Should have a winner"
    assert len(result.primary_result.final_candidates) >= 2, "Should have at least 2 final candidates"
    assert result.primary_result.democratic_winner is not None, "Should have a Democratic winner"
    assert result.primary_result.republican_winner is not None, "Should have a Republican winner"
    
    # Verify final candidates include party winners and independents
    final_candidate_names = [c.name for c in result.primary_result.final_candidates]
    assert result.primary_result.democratic_winner.name in final_candidate_names, "Democratic winner should be in final candidates"
    assert result.primary_result.republican_winner.name in final_candidate_names, "Republican winner should be in final candidates"
    
    # Check for independent candidate
    independent_candidates = [c for c in result.primary_result.final_candidates if c.tag == INDEPENDENTS]
    assert len(independent_candidates) >= 1, "Should have independent candidates in final list"
